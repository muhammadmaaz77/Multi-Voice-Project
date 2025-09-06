"""
Emotion Detection Service
Identifies basic emotions from text analysis.
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class EmotionType(Enum):
    """Basic emotion types."""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CONFUSED = "confused"

@dataclass
class EmotionResult:
    """Emotion detection result."""
    primary_emotion: EmotionType
    confidence: float
    emotion_scores: Dict[str, float]
    detected_indicators: List[str]

class EmotionDetector:
    """
    Basic emotion detection from text patterns and keywords.
    """
    
    def __init__(self):
        self.emotion_keywords = {
            EmotionType.HAPPY: [
                'happy', 'joy', 'excited', 'great', 'awesome', 'wonderful',
                'fantastic', 'amazing', 'love', 'perfect', 'excellent',
                'brilliant', 'good', 'nice', 'smile', 'laugh', 'haha',
                'lol', 'yay', 'hooray', 'celebrate'
            ],
            EmotionType.SAD: [
                'sad', 'cry', 'tears', 'depressed', 'down', 'upset',
                'disappointed', 'hurt', 'painful', 'sorry', 'regret',
                'miss', 'lonely', 'empty', 'hopeless', 'tragic',
                'unfortunate', 'terrible', 'awful', 'horrible'
            ],
            EmotionType.ANGRY: [
                'angry', 'mad', 'furious', 'rage', 'hate', 'annoyed',
                'frustrated', 'irritated', 'outraged', 'disgusted',
                'stupid', 'idiot', 'damn', 'hell', 'ridiculous',
                'unacceptable', 'outrageous', 'infuriating'
            ],
            EmotionType.EXCITED: [
                'excited', 'thrilled', 'pumped', 'energetic', 'eager',
                'enthusiastic', 'amazing', 'incredible', 'wow',
                'omg', 'awesome', 'fantastic', 'can\'t wait'
            ],
            EmotionType.CONFUSED: [
                'confused', 'puzzled', 'lost', 'unclear', 'huh',
                'what', 'don\'t understand', 'complicated', 'complex',
                'uncertain', 'doubt', 'questionable', 'strange'
            ]
        }
        
        self.emotion_patterns = {
            EmotionType.HAPPY: [
                r':\)', r':-\)', r':D', r'😊', r'😄', r'😃',
                r'\bhaha\b', r'\blol\b', r'\byay\b'
            ],
            EmotionType.SAD: [
                r':\(', r':-\(', r':\'', r'😢', r'😭', r'😞',
                r'\*sigh\*', r'\bcry\b'
            ],
            EmotionType.ANGRY: [
                r'>:\(', r'😠', r'😡', r'!{2,}', r'[A-Z]{3,}',
                r'\bdamn\b', r'\bhell\b'
            ],
            EmotionType.EXCITED: [
                r'!{1,}', r'😆', r'🎉', r'💫', r'\bwow\b',
                r'\bomg\b', r'\bawesome\b'
            ]
        }
    
    def detect_emotion(self, text: str, context: Dict = None) -> EmotionResult:
        """
        Detect emotion from text analysis.
        
        Args:
            text: Input text to analyze
            context: Optional context information
            
        Returns:
            EmotionResult with detected emotion and metadata
        """
        emotion_scores = {}
        detected_indicators = []
        
        # Analyze keywords
        for emotion, keywords in self.emotion_keywords.items():
            score = self._calculate_keyword_score(text.lower(), keywords)
            emotion_scores[emotion.value] = score
            
            # Track which keywords were found
            found_keywords = [kw for kw in keywords if kw in text.lower()]
            if found_keywords:
                detected_indicators.extend(found_keywords)
        
        # Analyze patterns
        for emotion, patterns in self.emotion_patterns.items():
            pattern_score = self._calculate_pattern_score(text, patterns)
            emotion_scores[emotion.value] += pattern_score * 0.5
        
        # Analyze punctuation and capitalization
        punctuation_emotion, punctuation_score = self._analyze_punctuation(text)
        if punctuation_emotion:
            emotion_scores[punctuation_emotion.value] += punctuation_score
        
        # Determine primary emotion
        if not emotion_scores or max(emotion_scores.values()) < 0.1:
            primary_emotion = EmotionType.NEUTRAL
            confidence = 0.9
        else:
            primary_emotion_str = max(emotion_scores.keys(), key=lambda k: emotion_scores[k])
            primary_emotion = EmotionType(primary_emotion_str)
            confidence = min(0.95, emotion_scores[primary_emotion_str])
        
        # Ensure neutral has a score
        if EmotionType.NEUTRAL.value not in emotion_scores:
            emotion_scores[EmotionType.NEUTRAL.value] = 0.1
        
        return EmotionResult(
            primary_emotion=primary_emotion,
            confidence=confidence,
            emotion_scores=emotion_scores,
            detected_indicators=detected_indicators
        )
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate emotion score based on keyword matches."""
        matches = sum(1 for keyword in keywords if keyword in text)
        word_count = len(text.split())
        return min(1.0, matches / max(word_count * 0.1, 1))
    
    def _calculate_pattern_score(self, text: str, patterns: List[str]) -> float:
        """Calculate emotion score based on pattern matches."""
        matches = sum(1 for pattern in patterns if re.search(pattern, text))
        return min(0.5, matches * 0.2)
    
    def _analyze_punctuation(self, text: str) -> Tuple[EmotionType, float]:
        """Analyze punctuation patterns for emotion indicators."""
        # Multiple exclamation marks = excited/happy
        if re.search(r'!{2,}', text):
            return EmotionType.EXCITED, 0.3
        
        # Question marks might indicate confusion
        question_ratio = text.count('?') / max(len(text), 1)
        if question_ratio > 0.1:
            return EmotionType.CONFUSED, 0.2
        
        # All caps might indicate anger or excitement
        caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
        if caps_words:
            return EmotionType.ANGRY, 0.3
        
        return None, 0.0
    
    def get_emotion_summary(self, emotion_result: EmotionResult) -> str:
        """Generate a human-readable emotion summary."""
        primary = emotion_result.primary_emotion.value
        confidence = emotion_result.confidence
        
        if confidence > 0.7:
            intensity = "strong"
        elif confidence > 0.4:
            intensity = "moderate"
        else:
            intensity = "slight"
        
        return f"{intensity} {primary} (confidence: {confidence:.2f})"

# Global emotion detector instance
emotion_detector = EmotionDetector()
