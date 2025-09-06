"""
Configuration module for Voice AI Bot Backend - Phase 4
Centralized configuration management for all phases.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    API_KEY: str = os.getenv("API_KEY")
    
    # Audio Processing Settings
    ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".webm"}
    DEFAULT_WHISPER_MODEL = "whisper-large-v3"
    
    # Chat Settings
    DEFAULT_CHAT_MODEL = "llama3-8b-8192"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 512
    
    # Phase 4 Settings
    SESSION_TIMEOUT_HOURS = 24
    RATE_LIMIT_PER_HOUR = 100
    LOGS_DIRECTORY = "logs"
    
    # Language Settings
    SUPPORTED_LANGUAGES = {
        "auto": "Auto-detect",
        "en": "English",
        "es": "Spanish", 
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean"
    }
    
    # Voice Settings
    VOICE_PREFERENCES = {
        "default": "Default Voice",
        "male_formal": "Male Formal",
        "female_warm": "Female Warm", 
        "neutral_professional": "Neutral Professional",
        "energetic_young": "Energetic Young"
    }
    
    def __init__(self):
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required")
        if not self.API_KEY:
            raise ValueError("API_KEY environment variable is required")

# Global settings instance
settings = Settings()
