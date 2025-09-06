"""
Persistent Memory Service - Phase 5B
Stores and retrieves session summaries from database
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from sqlalchemy.orm import Session
    from app.db import DatabaseService, get_db
    HAS_DATABASE = True
except ImportError:
    Session = None
    DatabaseService = None
    get_db = None
    HAS_DATABASE = False

from app.services.multiparty import multiparty_manager

class PersistentMemoryService:
    """Service for managing persistent conversation memory"""
    
    def __init__(self):
        self.db_service = DatabaseService() if HAS_DATABASE else None
    
    def store_session_summary(self, db, session_id: str, participants: List[Dict[str, Any]],
                            messages: List[Dict[str, Any]]) -> bool:
        """Store session summary in database"""
        if not self.db_service:
            print(f"📝 Mock: Stored summary for session {session_id}")
            return True
        
        try:
            # Generate summary from messages
            summary = self._generate_session_summary(messages, participants)
            
            # Store in database
            success = self.db_service.update_session_summary(db, session_id, summary)
            
            if success:
                print(f"💾 Stored session summary: {session_id}")
                return True
            else:
                print(f"❌ Failed to store summary: {session_id}")
                return False
                
        except Exception as e:
            print(f"Error storing session summary: {e}")
            return False
    
    def _generate_session_summary(self, messages: List[Dict[str, Any]], 
                                participants: List[Dict[str, Any]]) -> str:
        """Generate a simple summary from conversation messages"""
        if not messages:
            return "Empty conversation session"
        
        participant_names = [p.get("name", p.get("speaker_id")) for p in participants]
        message_count = len(messages)
        
        # Simple summary generation
        summary_parts = [
            f"Conversation with {len(participants)} participants: {', '.join(participant_names)}",
            f"Total messages: {message_count}",
            f"Duration: {self._calculate_duration(messages)}",
        ]
        
        # Add sample of conversation
        if messages:
            summary_parts.append("Key points:")
            for i, msg in enumerate(messages[:3]):  # First 3 messages
                speaker = msg.get("speaker_id", "Unknown")
                content = msg.get("content", "")[:100]  # First 100 chars
                summary_parts.append(f"- {speaker}: {content}...")
        
        return "\n".join(summary_parts)
    
    def _calculate_duration(self, messages: List[Dict[str, Any]]) -> str:
        """Calculate conversation duration"""
        if len(messages) < 2:
            return "< 1 minute"
        
        try:
            first_time = datetime.fromisoformat(messages[0]["timestamp"].replace("Z", "+00:00"))
            last_time = datetime.fromisoformat(messages[-1]["timestamp"].replace("Z", "+00:00"))
            duration = last_time - first_time
            
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes} minutes" if minutes > 0 else "< 1 minute"
        except:
            return "Unknown duration"
    
    def get_session_summary(self, db, session_id: str) -> Optional[str]:
        """Retrieve session summary from database"""
        if not self.db_service:
            return f"Mock summary for session {session_id}"
        
        try:
            # Get session messages to generate/update summary
            messages = self.db_service.get_session_messages(db, session_id)
            
            if messages:
                # Get session info from multiparty manager
                session_info = multiparty_manager.get_session_info(session_id)
                participants = session_info.get("participants", []) if session_info else []
                
                # Generate fresh summary
                return self._generate_session_summary(messages, participants)
            
            return None
        except Exception as e:
            print(f"Error getting session summary: {e}")
            return None
    
    def get_user_last_session_summary(self, db, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the last session summary for a user"""
        if not self.db_service:
            return {
                "session_id": "mock_session",
                "summary": f"Previous conversation summary for user {user_id}",
                "participants": ["user", "assistant"],
                "date": datetime.utcnow().isoformat()
            }
        
        try:
            last_session = self.db_service.get_user_last_session(db, user_id)
            return last_session
        except Exception as e:
            print(f"Error getting user last session: {e}")
            return None
    
    def store_conversation_context(self, db, session_id: str, user_id: str, 
                                 participants: List[Dict[str, Any]]) -> bool:
        """Store conversation context when session starts"""
        if not self.db_service:
            print(f"📝 Mock: Stored context for session {session_id}")
            return True
        
        try:
            success = self.db_service.create_conversation_session(
                db, session_id, user_id, participants
            )
            
            if success:
                print(f"💾 Stored conversation context: {session_id}")
                return True
            else:
                print(f"❌ Failed to store context: {session_id}")
                return False
                
        except Exception as e:
            print(f"Error storing conversation context: {e}")
            return False
    
    def add_message_to_history(self, db, session_id: str, speaker_id: str, 
                             content: str, message_type: str = "transcription", 
                             language: str = "en", emotions: Optional[Dict] = None) -> bool:
        """Add a message to persistent history"""
        if not self.db_service:
            print(f"📝 Mock: Added message from {speaker_id}: {content[:50]}...")
            return True
        
        try:
            success = self.db_service.add_message(
                db, session_id, speaker_id, content, 
                message_type, language, emotions
            )
            
            return success
        except Exception as e:
            print(f"Error adding message to history: {e}")
            return False
    
    def get_session_analytics(self, db, session_id: str) -> Dict[str, Any]:
        """Get analytics for a session"""
        try:
            messages = self.db_service.get_session_messages(db, session_id) if self.db_service else []
            session_info = multiparty_manager.get_session_info(session_id)
            
            if not messages and not session_info:
                return {"error": "Session not found"}
            
            # Calculate basic analytics
            analytics = {
                "session_id": session_id,
                "message_count": len(messages),
                "participant_count": len(session_info.get("participants", [])) if session_info else 0,
                "duration": self._calculate_duration(messages),
                "languages_used": list(set(msg.get("language", "en") for msg in messages)),
                "message_types": {}
            }
            
            # Count message types
            for msg in messages:
                msg_type = msg.get("message_type", "unknown")
                analytics["message_types"][msg_type] = analytics["message_types"].get(msg_type, 0) + 1
            
            return analytics
            
        except Exception as e:
            print(f"Error getting session analytics: {e}")
            return {"error": str(e)}
    
    def cleanup_old_sessions(self, db, days_old: int = 30) -> int:
        """Clean up old sessions (placeholder for future implementation)"""
        # This would be implemented to clean up sessions older than X days
        print(f"🧹 Mock: Would clean up sessions older than {days_old} days")
        return 0

# Global persistent memory service instance
persistent_memory_service = PersistentMemoryService()
