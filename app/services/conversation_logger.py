"""
Conversation History Logging Service for Phase 4
Manages session-based conversation storage and retrieval.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ConversationEntry:
    """Single conversation entry."""
    timestamp: str
    session_id: str
    speaker_id: str
    speaker_label: str
    original_text: str
    translated_text: Optional[str]
    source_language: Optional[str]
    target_language: Optional[str]
    emotion: str
    emotion_confidence: float
    audio_file_path: Optional[str] = None

@dataclass
class ConversationSession:
    """Complete conversation session."""
    session_id: str
    start_time: str
    end_time: Optional[str]
    source_language: str
    target_language: str
    participant_count: int
    total_entries: int
    entries: List[ConversationEntry]

class ConversationLogger:
    """
    Manages conversation history logging with session-based storage.
    """
    
    def __init__(self, logs_directory: str = "logs"):
        self.logs_dir = logs_directory
        self._ensure_logs_directory()
        self.active_sessions: Dict[str, ConversationSession] = {}
    
    def _ensure_logs_directory(self):
        """Ensure logs directory exists."""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
    
    def start_session(self, 
                     session_id: str, 
                     source_language: str = "auto", 
                     target_language: str = "en") -> ConversationSession:
        """
        Start a new conversation session.
        
        Args:
            session_id: Unique session identifier
            source_language: Source language code
            target_language: Target language code
            
        Returns:
            ConversationSession object
        """
        session = ConversationSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            source_language=source_language,
            target_language=target_language,
            participant_count=0,
            total_entries=0,
            entries=[]
        )
        
        self.active_sessions[session_id] = session
        return session
    
    def log_conversation(self,
                        session_id: str,
                        speaker_id: str,
                        speaker_label: str,
                        original_text: str,
                        emotion: str,
                        emotion_confidence: float,
                        translated_text: Optional[str] = None,
                        audio_file_path: Optional[str] = None) -> bool:
        """
        Log a conversation entry.
        
        Args:
            session_id: Session identifier
            speaker_id: Unique speaker identifier
            speaker_label: Human-readable speaker label
            original_text: Original transcribed text
            emotion: Detected emotion
            emotion_confidence: Emotion detection confidence
            translated_text: Translated text (if applicable)
            audio_file_path: Path to audio file (if saved)
            
        Returns:
            True if logged successfully, False otherwise
        """
        if session_id not in self.active_sessions:
            # Try to load existing session or create new one
            session = self._load_or_create_session(session_id)
        else:
            session = self.active_sessions[session_id]
        
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            speaker_id=speaker_id,
            speaker_label=speaker_label,
            original_text=original_text,
            translated_text=translated_text,
            source_language=session.source_language,
            target_language=session.target_language,
            emotion=emotion,
            emotion_confidence=emotion_confidence,
            audio_file_path=audio_file_path
        )
        
        session.entries.append(entry)
        session.total_entries += 1
        
        # Update participant count if new speaker
        existing_speakers = {e.speaker_id for e in session.entries}
        session.participant_count = len(existing_speakers)
        
        # Save to file immediately for persistence
        self._save_session_to_file(session)
        
        return True
    
    def end_session(self, session_id: str) -> bool:
        """
        End a conversation session.
        
        Args:
            session_id: Session to end
            
        Returns:
            True if ended successfully, False if session not found
        """
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.now().isoformat()
        
        # Final save
        self._save_session_to_file(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        return True
    
    def get_session_history(self, session_id: str) -> Optional[ConversationSession]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationSession or None if not found
        """
        # Check active sessions first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Try to load from file
        return self._load_session_from_file(session_id)
    
    def get_recent_sessions(self, limit: int = 10) -> List[str]:
        """
        Get list of recent session IDs.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session IDs, most recent first
        """
        log_files = []
        
        for filename in os.listdir(self.logs_dir):
            if filename.endswith('.json') and filename.startswith('session_'):
                file_path = os.path.join(self.logs_dir, filename)
                session_id = filename.replace('session_', '').replace('.json', '')
                modified_time = os.path.getmtime(file_path)
                log_files.append((session_id, modified_time))
        
        # Sort by modification time, most recent first
        log_files.sort(key=lambda x: x[1], reverse=True)
        
        return [session_id for session_id, _ in log_files[:limit]]
    
    def _load_or_create_session(self, session_id: str) -> ConversationSession:
        """Load existing session or create new one."""
        existing_session = self._load_session_from_file(session_id)
        if existing_session:
            self.active_sessions[session_id] = existing_session
            return existing_session
        
        return self.start_session(session_id)
    
    def _save_session_to_file(self, session: ConversationSession):
        """Save session to JSON file."""
        filename = f"session_{session.session_id}.json"
        file_path = os.path.join(self.logs_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(session), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving session {session.session_id}: {e}")
    
    def _load_session_from_file(self, session_id: str) -> Optional[ConversationSession]:
        """Load session from JSON file."""
        filename = f"session_{session_id}.json"
        file_path = os.path.join(self.logs_dir, filename)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Convert entries back to ConversationEntry objects
            entries = [ConversationEntry(**entry) for entry in data['entries']]
            data['entries'] = entries
            
            return ConversationSession(**data)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def export_session(self, session_id: str, format: str = "json") -> str:
        """
        Export session in specified format.
        
        Args:
            session_id: Session to export
            format: Export format ("json", "txt", "csv")
            
        Returns:
            Exported content as string
        """
        session = self.get_session_history(session_id)
        if not session:
            return ""
        
        if format == "txt":
            return self._export_as_text(session)
        elif format == "csv":
            return self._export_as_csv(session)
        else:  # default to json
            return json.dumps(asdict(session), indent=2, ensure_ascii=False)
    
    def _export_as_text(self, session: ConversationSession) -> str:
        """Export session as readable text."""
        lines = [
            f"Conversation Session: {session.session_id}",
            f"Started: {session.start_time}",
            f"Languages: {session.source_language} → {session.target_language}",
            f"Participants: {session.participant_count}",
            f"Total Entries: {session.total_entries}",
            "=" * 50,
            ""
        ]
        
        for entry in session.entries:
            lines.extend([
                f"[{entry.timestamp}] {entry.speaker_label}:",
                f"  Original: {entry.original_text}",
                f"  Emotion: {entry.emotion} ({entry.emotion_confidence:.2f})",
                ""
            ])
            
            if entry.translated_text:
                lines.insert(-1, f"  Translation: {entry.translated_text}")
        
        return "\n".join(lines)
    
    def _export_as_csv(self, session: ConversationSession) -> str:
        """Export session as CSV."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "timestamp", "speaker_label", "original_text", 
            "translated_text", "emotion", "emotion_confidence"
        ])
        
        # Data rows
        for entry in session.entries:
            writer.writerow([
                entry.timestamp,
                entry.speaker_label,
                entry.original_text,
                entry.translated_text or "",
                entry.emotion,
                entry.emotion_confidence
            ])
        
        return output.getvalue()

# Global conversation logger instance
conversation_logger = ConversationLogger("logs")
