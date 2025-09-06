"""
Database operations for Phase 5B
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    from sqlalchemy.orm import Session
    from .models import ConversationSession, ConversationMessage, SpeakerProfile
    from .database import SQLALCHEMY_AVAILABLE
except ImportError:
    Session = None
    ConversationSession = None
    ConversationMessage = None
    SpeakerProfile = None
    SQLALCHEMY_AVAILABLE = False

class DatabaseService:
    """Service for handling database operations"""
    
    def create_conversation_session(self, db, session_id: str, user_id: str, 
                                  participants: List[Dict[str, Any]]) -> bool:
        """Create a new conversation session"""
        if not SQLALCHEMY_AVAILABLE or not db:
            print(f"📝 Mock: Created session {session_id} for user {user_id}")
            return True
            
        try:
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id,
                participants=participants,
                metadata={"created_via": "api"}
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            db.rollback()
            return False
    
    def add_message(self, db, session_id: str, speaker_id: str, 
                   content: str, message_type: str = "transcription", 
                   language: str = "en", emotions: Optional[Dict] = None) -> bool:
        """Add a message to a conversation session"""
        if not SQLALCHEMY_AVAILABLE or not db:
            print(f"📝 Mock: Added message from {speaker_id}: {content[:50]}...")
            return True
            
        try:
            message = ConversationMessage(
                session_id=session_id,
                speaker_id=speaker_id,
                message_type=message_type,
                content=content,
                language=language,
                emotions=emotions or {},
                metadata={"processed_at": datetime.utcnow().isoformat()}
            )
            db.add(message)
            db.commit()
            return True
        except Exception as e:
            print(f"Error adding message: {e}")
            db.rollback()
            return False
    
    def get_session_messages(self, db, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session"""
        if not SQLALCHEMY_AVAILABLE or not db:
            return [
                {
                    "speaker_id": "mock_user",
                    "content": "Mock conversation message",
                    "timestamp": datetime.utcnow().isoformat(),
                    "message_type": "transcription"
                }
            ]
            
        try:
            messages = db.query(ConversationMessage).filter(
                ConversationMessage.session_id == session_id
            ).order_by(ConversationMessage.timestamp).all()
            
            return [
                {
                    "speaker_id": msg.speaker_id,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "message_type": msg.message_type,
                    "language": msg.language,
                    "emotions": msg.emotions
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    def update_session_summary(self, db, session_id: str, summary: str) -> bool:
        """Update session summary"""
        if not SQLALCHEMY_AVAILABLE or not db:
            print(f"📝 Mock: Updated summary for session {session_id}")
            return True
            
        try:
            session = db.query(ConversationSession).filter(
                ConversationSession.session_id == session_id
            ).first()
            
            if session:
                session.summary = summary
                session.updated_at = datetime.utcnow()
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating summary: {e}")
            db.rollback()
            return False
    
    def get_user_last_session(self, db, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's last session summary"""
        if not SQLALCHEMY_AVAILABLE or not db:
            return {
                "session_id": "mock_session",
                "summary": "Mock session summary for user context",
                "participants": ["user1", "assistant"],
                "created_at": datetime.utcnow().isoformat()
            }
            
        try:
            session = db.query(ConversationSession).filter(
                ConversationSession.user_id == user_id
            ).order_by(ConversationSession.updated_at.desc()).first()
            
            if session and session.summary:
                return {
                    "session_id": session.session_id,
                    "summary": session.summary,
                    "participants": session.participants,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat()
                }
            return None
        except Exception as e:
            print(f"Error getting last session: {e}")
            return None

# Create global instance
db_service = DatabaseService()
