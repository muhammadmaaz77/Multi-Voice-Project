"""
Database models for Phase 5B
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
    from sqlalchemy.orm import relationship
    from .database import Base, SQLALCHEMY_AVAILABLE
    
    if not SQLALCHEMY_AVAILABLE:
        # Create dummy base if SQLAlchemy is not available
        class Base:
            pass
        
        # Create dummy functions
        def Column(*args, **kwargs): return None
        def relationship(*args, **kwargs): return None
        String = Text = DateTime = JSON = ForeignKey = Integer = None
        
except ImportError:
    # Handle missing SQLAlchemy gracefully
    SQLALCHEMY_AVAILABLE = False
    class Base:
        pass
    
    def Column(*args, **kwargs): return None
    def relationship(*args, **kwargs): return None
    String = Text = DateTime = JSON = ForeignKey = Integer = None

# Only define models if SQLAlchemy is available
if SQLALCHEMY_AVAILABLE:
    class ConversationSession(Base):
        """Table for storing conversation sessions"""
        __tablename__ = "conversation_sessions"
        
        id = Column(Integer, primary_key=True, index=True)
        session_id = Column(String(255), unique=True, index=True, nullable=False)
        user_id = Column(String(255), index=True)
        participants = Column(JSON)  # List of participant info
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        status = Column(String(50), default="active")
        summary = Column(Text)
        session_metadata = Column(JSON)  # Renamed to avoid SQLAlchemy conflict
        
        # Relationship to messages
        messages = relationship("ConversationMessage", back_populates="session")

    class ConversationMessage(Base):
        """Table for storing individual messages"""
        __tablename__ = "conversation_messages"
        
        id = Column(Integer, primary_key=True, index=True)
        session_id = Column(String(255), ForeignKey("conversation_sessions.session_id"))
        speaker_id = Column(String(255), nullable=False)
        message_type = Column(String(50))  # 'transcription', 'response', 'translation'
        content = Column(Text, nullable=False)
        timestamp = Column(DateTime, default=datetime.utcnow)
        language = Column(String(10))
        emotions = Column(JSON)
        message_metadata = Column(JSON)  # Renamed to avoid SQLAlchemy conflict
        
        # Relationship to session
        session = relationship("ConversationSession", back_populates="messages")

    class SpeakerProfile(Base):
        """Table for storing speaker profiles"""
        __tablename__ = "speaker_profiles"
        
        id = Column(Integer, primary_key=True, index=True)
        speaker_id = Column(String(255), unique=True, index=True, nullable=False)
        name = Column(String(255))
        voice_characteristics = Column(JSON)
        language_preferences = Column(JSON)
        created_at = Column(DateTime, default=datetime.utcnow)
        last_active = Column(DateTime, default=datetime.utcnow)
        total_sessions = Column(Integer, default=0)
        speaker_metadata = Column(JSON)  # Renamed to avoid SQLAlchemy conflict

else:
    # Create dummy classes when SQLAlchemy is not available
    class ConversationSession:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class ConversationMessage:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class SpeakerProfile:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
