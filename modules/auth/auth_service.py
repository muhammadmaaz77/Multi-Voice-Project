"""
Enhanced Authentication Service for Phase 4
Manages API keys, sessions, and user access control.
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
from dataclasses import dataclass

@dataclass
class SessionInfo:
    """Information about an active session."""
    session_id: str
    api_key: str
    created_at: datetime
    last_activity: datetime
    request_count: int
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    user_preferences: Dict = None

@dataclass
class APIKeyInfo:
    """Information about an API key."""
    key_hash: str
    name: str
    created_at: datetime
    last_used: datetime
    request_count: int
    is_active: bool
    rate_limit: int = 100  # requests per hour

class EnhancedAuthService:
    """
    Enhanced authentication service with session management.
    """
    
    def __init__(self):
        self.valid_api_keys: Set[str] = set()
        self.api_key_info: Dict[str, APIKeyInfo] = {}
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.rate_limits: Dict[str, Dict] = {}
        
        # Load default API key from config
        self._load_default_api_keys()
    
    def _load_default_api_keys(self):
        """Load default API keys from environment/config."""
        try:
            from config.settings import settings
            default_key = settings.API_KEY
            if default_key:
                self.add_api_key(default_key, "Default API Key")
        except ImportError:
            # Fallback to direct environment variable
            import os
            from dotenv import load_dotenv
            load_dotenv()
            default_key = os.getenv("API_KEY")
            if default_key:
                self.add_api_key(default_key, "Default API Key")
        
        # Also add the test key for validation
        self.add_api_key("fast_API_KEY", "Test API Key")
    
    def add_api_key(self, api_key: str, name: str = "API Key") -> str:
        """
        Add a new API key to the system.
        
        Args:
            api_key: The API key string
            name: Human-readable name for the key
            
        Returns:
            Key hash for tracking
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        
        self.valid_api_keys.add(api_key)
        self.api_key_info[api_key] = APIKeyInfo(
            key_hash=key_hash,
            name=name,
            created_at=datetime.now(),
            last_used=datetime.now(),
            request_count=0,
            is_active=True
        )
        
        return key_hash
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate an API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not api_key or api_key not in self.valid_api_keys:
            return False
        
        # Check if key is active
        key_info = self.api_key_info.get(api_key)
        if not key_info or not key_info.is_active:
            return False
        
        # Check rate limits
        if not self._check_rate_limit(api_key):
            return False
        
        # Update usage statistics
        self._update_key_usage(api_key)
        
        return True
    
    def create_session(self, api_key: str, preferences: Dict = None) -> str:
        """
        Create a new session for an authenticated user.
        
        Args:
            api_key: Valid API key
            preferences: User preferences (language, voice, etc.)
            
        Returns:
            Session ID
        """
        if not self.validate_api_key(api_key):
            raise ValueError("Invalid API key")
        
        session_id = secrets.token_urlsafe(32)
        
        self.active_sessions[session_id] = SessionInfo(
            session_id=session_id,
            api_key=api_key,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            request_count=0,
            user_preferences=preferences or {}
        )
        
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """
        Validate an active session.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Check if session is expired (24 hours)
        if datetime.now() - session.created_at > timedelta(hours=24):
            self.end_session(session_id)
            return False
        
        # Update last activity
        session.last_activity = datetime.now()
        session.request_count += 1
        
        return True
    
    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information."""
        return self.active_sessions.get(session_id)
    
    def update_session_preferences(self, session_id: str, preferences: Dict):
        """Update session preferences."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.user_preferences.update(preferences)
    
    def end_session(self, session_id: str) -> bool:
        """
        End an active session.
        
        Args:
            session_id: Session ID to end
            
        Returns:
            True if session was ended, False if not found
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
    
    def _check_rate_limit(self, api_key: str) -> bool:
        """Check if API key has exceeded rate limits."""
        now = datetime.now()
        hour_key = now.strftime("%Y-%m-%d-%H")
        
        if api_key not in self.rate_limits:
            self.rate_limits[api_key] = {}
        
        key_limits = self.rate_limits[api_key]
        
        # Clean old entries
        old_keys = [k for k in key_limits.keys() if k != hour_key]
        for old_key in old_keys:
            del key_limits[old_key]
        
        # Check current hour limit
        current_requests = key_limits.get(hour_key, 0)
        rate_limit = self.api_key_info[api_key].rate_limit
        
        if current_requests >= rate_limit:
            return False
        
        # Increment counter
        key_limits[hour_key] = current_requests + 1
        return True
    
    def _update_key_usage(self, api_key: str):
        """Update API key usage statistics."""
        if api_key in self.api_key_info:
            info = self.api_key_info[api_key]
            info.last_used = datetime.now()
            info.request_count += 1
    
    def get_api_key_stats(self, api_key: str) -> Optional[APIKeyInfo]:
        """Get statistics for an API key."""
        return self.api_key_info.get(api_key)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        return len(self.active_sessions)
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        now = datetime.now()
        expired_sessions = [
            sid for sid, session in self.active_sessions.items()
            if now - session.created_at > timedelta(hours=24)
        ]
        
        for session_id in expired_sessions:
            self.end_session(session_id)

# Global enhanced auth service instance
enhanced_auth_service = EnhancedAuthService()
