"""
Multiparty Conversation Service - Phase 5B
Handles up to 4 speakers in the same session
"""
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import asyncio
import json

class MultipartySession:
    """Represents a multiparty conversation session"""
    
    def __init__(self, session_id: str, max_participants: int = 4):
        self.session_id = session_id
        self.max_participants = max_participants
        self.participants: Dict[str, Dict[str, Any]] = {}
        self.websockets: Dict[str, Any] = {}  # speaker_id -> websocket
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.conversation_history: List[Dict[str, Any]] = []
        
    def add_participant(self, speaker_id: str, websocket, participant_info: Dict[str, Any]) -> bool:
        """Add a participant to the session"""
        if len(self.participants) >= self.max_participants:
            return False
            
        self.participants[speaker_id] = {
            "speaker_id": speaker_id,
            "joined_at": datetime.utcnow().isoformat(),
            "language": participant_info.get("language", "en"),
            "name": participant_info.get("name", f"Speaker {speaker_id}"),
            "metadata": participant_info.get("metadata", {})
        }
        self.websockets[speaker_id] = websocket
        self.last_activity = datetime.utcnow()
        return True
    
    def remove_participant(self, speaker_id: str):
        """Remove a participant from the session"""
        self.participants.pop(speaker_id, None)
        self.websockets.pop(speaker_id, None)
        self.last_activity = datetime.utcnow()
    
    def get_participant_count(self) -> int:
        """Get number of active participants"""
        return len(self.participants)
    
    def get_participant_list(self) -> List[Dict[str, Any]]:
        """Get list of all participants"""
        return list(self.participants.values())
    
    async def broadcast_message(self, message: Dict[str, Any], exclude_speaker: Optional[str] = None):
        """Broadcast message to all participants except the sender"""
        for speaker_id, websocket in self.websockets.items():
            if exclude_speaker and speaker_id == exclude_speaker:
                continue
                
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error broadcasting to {speaker_id}: {e}")
                # Remove disconnected websocket
                self.remove_participant(speaker_id)
    
    def add_to_history(self, speaker_id: str, content: str, message_type: str = "transcription"):
        """Add message to conversation history"""
        self.conversation_history.append({
            "speaker_id": speaker_id,
            "content": content,
            "message_type": message_type,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.last_activity = datetime.utcnow()

class MultipartyManager:
    """Manages multiple multiparty sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, MultipartySession] = {}
        self.speaker_to_session: Dict[str, str] = {}  # speaker_id -> session_id
    
    def create_session(self, session_id: str, max_participants: int = 4) -> MultipartySession:
        """Create a new multiparty session"""
        if session_id in self.sessions:
            return self.sessions[session_id]
            
        session = MultipartySession(session_id, max_participants)
        self.sessions[session_id] = session
        print(f"🎭 Created multiparty session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[MultipartySession]:
        """Get an existing session"""
        return self.sessions.get(session_id)
    
    def join_session(self, session_id: str, speaker_id: str, websocket, 
                    participant_info: Dict[str, Any]) -> bool:
        """Join a speaker to a session"""
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)
        
        # Check if speaker is already in another session
        if speaker_id in self.speaker_to_session:
            old_session_id = self.speaker_to_session[speaker_id]
            self.leave_session(old_session_id, speaker_id)
        
        success = session.add_participant(speaker_id, websocket, participant_info)
        if success:
            self.speaker_to_session[speaker_id] = session_id
            print(f"👤 Speaker {speaker_id} joined session {session_id}")
            return True
        
        print(f"❌ Failed to add speaker {speaker_id} to session {session_id} (session full)")
        return False
    
    def leave_session(self, session_id: str, speaker_id: str):
        """Remove speaker from session"""
        session = self.get_session(session_id)
        if session:
            session.remove_participant(speaker_id)
            self.speaker_to_session.pop(speaker_id, None)
            print(f"👋 Speaker {speaker_id} left session {session_id}")
            
            # Clean up empty sessions
            if session.get_participant_count() == 0:
                self.sessions.pop(session_id, None)
                print(f"🗑️ Cleaned up empty session {session_id}")
    
    async def process_speaker_message(self, session_id: str, speaker_id: str, 
                                    content: str, message_type: str = "transcription") -> Dict[str, Any]:
        """Process message from a speaker and broadcast to others"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Add to session history
        session.add_to_history(speaker_id, content, message_type)
        
        # Create broadcast message
        broadcast_message = {
            "type": "multiparty_message",
            "session_id": session_id,
            "speaker_id": speaker_id,
            "content": content,
            "message_type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
            "participants": session.get_participant_list()
        }
        
        # Broadcast to other participants
        await session.broadcast_message(broadcast_message, exclude_speaker=speaker_id)
        
        return {
            "status": "broadcasted",
            "participants_notified": session.get_participant_count() - 1,
            "session_info": {
                "session_id": session_id,
                "participant_count": session.get_participant_count(),
                "participants": session.get_participant_list()
            }
        }
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session"""
        session = self.get_session(session_id)
        if not session:
            return None
            
        return {
            "session_id": session_id,
            "participant_count": session.get_participant_count(),
            "max_participants": session.max_participants,
            "participants": session.get_participant_list(),
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "conversation_length": len(session.conversation_history)
        }
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get information about all active sessions"""
        return [
            self.get_session_info(session_id) 
            for session_id in self.sessions.keys()
        ]

# Global multiparty manager instance
multiparty_manager = MultipartyManager()
