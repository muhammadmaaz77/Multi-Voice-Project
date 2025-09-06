"""
Database operations for Phase 5B - SQLAlchemy safe version
"""
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

from typing import List, Optional, Dict, Any
from datetime import datetime
import json

class DatabaseService:
    """Service for database operations with SQLAlchemy safety"""
    
    def __init__(self, db):
        if not SQLALCHEMY_AVAILABLE:
            self.db = None
            print("⚠️  Database service disabled - SQLAlchemy not available")
        else:
            self.db = db
    
    def _check_availability(self):
        """Check if database is available"""
        if not SQLALCHEMY_AVAILABLE:
            print("⚠️  Database operation skipped - SQLAlchemy not available")
            return False
        return True
    
    # Session operations
    def create_session(self, session_id: str, participants: List[Dict[str, Any]]):
        """Create a new conversation session"""
        if not self._check_availability():
            return None
            
        session = ConversationSession(
            session_id=session_id,
            participants=participants,
            summary="",
            status="active"
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session(self, session_id: str):
        """Get session by ID"""
        if not self._check_availability():
            return None
            
        return self.db.query(ConversationSession).filter(
            ConversationSession.session_id == session_id
        ).first()
    
    def update_session_summary(self, session_id: str, summary: str):
        """Update session summary"""
        if not self._check_availability():
            return False
            
        session = self.get_session(session_id)
        if session:
            session.summary = summary
            session.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def get_user_last_session(self, user_id: str):
        """Get user's last session"""
        if not self._check_availability():
            return None
            
        # Find sessions where user is in participants
        sessions = self.db.query(ConversationSession).filter(
            ConversationSession.participants.contains([{"id": user_id}])
        ).order_by(ConversationSession.created_at.desc()).first()
        return sessions
    
    # Message operations
    def add_message(self, session_id: str, speaker_id: str, speaker_name: str,
                   message_type: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to session"""
        if not self._check_availability():
            return None
            
        message = ConversationMessage(
            session_id=session_id,
            speaker_id=speaker_id,
            speaker_name=speaker_name,
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_session_messages(self, session_id: str, limit: int = 100):
        """Get messages for a session"""
        if not self._check_availability():
            return []
            
        return self.db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).order_by(ConversationMessage.timestamp.desc()).limit(limit).all()
    
    # Speaker operations
    def create_speaker_profile(self, speaker_id: str, name: str,
                             language_preference: str = "en"):
        """Create speaker profile"""
        if not self._check_availability():
            return None
            
        # Check if profile already exists
        existing = self.get_speaker_profile(speaker_id)
        if existing:
            return existing
        
        profile = SpeakerProfile(
            speaker_id=speaker_id,
            name=name,
            language_preference=language_preference,
            voice_characteristics={}
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def update_speaker_characteristics(self, speaker_id: str, characteristics: Dict[str, Any]):
        """Update speaker voice characteristics"""
        if not self._check_availability():
            return False
            
        profile = self.get_speaker_profile(speaker_id)
        if profile:
            profile.voice_characteristics = characteristics
            self.db.commit()
            return True
        return False
    
    def get_speaker_profile(self, speaker_id: str):
        """Get speaker profile by ID"""
        if not self._check_availability():
            return None
            
        return self.db.query(SpeakerProfile).filter(
            SpeakerProfile.speaker_id == speaker_id
        ).first()
    
    # Analytics operations
    def get_session_analytics(self, session_id: str):
        """Get analytics for a session"""
        if not self._check_availability():
            return {}
            
        session = self.get_session(session_id)
        messages = self.get_session_messages(session_id)
        
        if not session:
            return {}
        
        analytics = {
            "session_duration": (datetime.utcnow() - session.created_at).total_seconds(),
            "message_count": len(messages),
            "participant_count": len(session.participants) if session.participants else 0,
            "message_types": {},
            "active_speakers": set()
        }
        
        # Analyze messages
        for message in messages:
            # Count message types
            msg_type = message.message_type
            analytics["message_types"][msg_type] = analytics["message_types"].get(msg_type, 0) + 1
            
            # Track active speakers
            analytics["active_speakers"].add(message.speaker_name)
        
        analytics["active_speakers"] = list(analytics["active_speakers"])
        
        return analytics
