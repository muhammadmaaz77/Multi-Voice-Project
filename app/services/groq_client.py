"""
Groq client initialization and configuration.
"""
from groq import Groq
from app.config import settings

# Initialize Groq client with API key from settings
groq_client = Groq(api_key=settings.GROQ_API_KEY)
