"""
Speaker Identification Service
Detects and maintains speaker separation throughout conversations.
"""
import hashlib
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class SpeakerInfo:
    """Information about an identified speaker."""
    speaker_id: str
    label: str
    confidence: float
    first_seen: str
    last_seen: str

class SpeakerIdentifier:
    """
    Speaker identification service that analyzes text patterns
    and maintains speaker consistency across conversations.
    """
    
    def __init__(self):
        self.speakers: Dict[str, SpeakerInfo] = {}
        self.speaker_counter = 0
        
    def identify_speaker(self, text: str, audio_features: Dict = None) -> Tuple[str, float]:
        """
        Identify speaker from text patterns and optional audio features.
        
        Args:
            text: Transcribed text
            audio_features: Optional audio characteristics (pitch, tone, etc.)
            
        Returns:
            Tuple of (speaker_id, confidence_score)
        """
        # Simple speaker identification based on text patterns and style
        speaker_signature = self._extract_speaker_signature(text)
        speaker_id = self._get_or_create_speaker(speaker_signature)
        confidence = self._calculate_confidence(text, speaker_signature)
        
        return speaker_id, confidence
    
    def _extract_speaker_signature(self, text: str) -> str:
        """
        Extract speaker signature from text patterns.
        
        Args:
            text: Input text
            
        Returns:
            Speaker signature hash
        """
        # Analyze text characteristics
        features = []
        
        # Sentence length patterns
        sentences = text.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        features.append(f"avg_len_{int(avg_length)}")
        
        # Common words and phrases
        common_words = ['um', 'uh', 'like', 'you know', 'I mean', 'actually']
        used_fillers = [word for word in common_words if word.lower() in text.lower()]
        features.extend(used_fillers)
        
        # Punctuation usage
        question_ratio = text.count('?') / max(len(text.split()), 1)
        exclamation_ratio = text.count('!') / max(len(text.split()), 1)
        features.append(f"q_{int(question_ratio*100)}")
        features.append(f"e_{int(exclamation_ratio*100)}")
        
        # Create signature hash
        signature = '_'.join(sorted(features))
        return hashlib.md5(signature.encode()).hexdigest()[:8]
    
    def _get_or_create_speaker(self, signature: str) -> str:
        """
        Get existing speaker or create new one.
        
        Args:
            signature: Speaker signature
            
        Returns:
            Speaker ID
        """
        # Check if we've seen this signature before
        for speaker_id, info in self.speakers.items():
            if signature in speaker_id:
                return speaker_id
        
        # Create new speaker
        self.speaker_counter += 1
        speaker_id = f"Speaker_{chr(64 + self.speaker_counter)}_{signature}"
        
        from datetime import datetime
        now = datetime.now().isoformat()
        
        self.speakers[speaker_id] = SpeakerInfo(
            speaker_id=speaker_id,
            label=f"Speaker {chr(64 + self.speaker_counter)}",
            confidence=0.8,
            first_seen=now,
            last_seen=now
        )
        
        return speaker_id
    
    def _calculate_confidence(self, text: str, signature: str) -> float:
        """
        Calculate confidence score for speaker identification.
        
        Args:
            text: Input text
            signature: Speaker signature
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        base_confidence = 0.7
        
        # Longer text = higher confidence
        length_bonus = min(0.2, len(text.split()) / 100)
        
        # Unique patterns = higher confidence
        unique_patterns = len(set(text.lower().split()))
        pattern_bonus = min(0.1, unique_patterns / 50)
        
        return min(1.0, base_confidence + length_bonus + pattern_bonus)
    
    def get_speaker_info(self, speaker_id: str) -> SpeakerInfo:
        """Get information about a specific speaker."""
        return self.speakers.get(speaker_id)
    
    def get_all_speakers(self) -> Dict[str, SpeakerInfo]:
        """Get all identified speakers."""
        return self.speakers.copy()
    
    def update_speaker_activity(self, speaker_id: str):
        """Update last seen timestamp for a speaker."""
        if speaker_id in self.speakers:
            from datetime import datetime
            self.speakers[speaker_id].last_seen = datetime.now().isoformat()

# Global speaker identifier instance
speaker_identifier = SpeakerIdentifier()
