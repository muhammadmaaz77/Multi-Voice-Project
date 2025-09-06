"""
Speech-to-Text service using Groq Whisper models.
"""
from fastapi import UploadFile
from app.config import settings
from app.services.groq_client import groq_client

def is_audio_file(filename: str) -> bool:
    """
    Validate if uploaded file is an audio file.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    if not filename:
        return False
    return any(filename.lower().endswith(ext) for ext in settings.ALLOWED_AUDIO_EXTENSIONS)

async def transcribe_audio(file: UploadFile) -> dict:
    """
    Transcribe audio file using Groq Whisper model.
    
    Args:
        file: Uploaded audio file
        
    Returns:
        dict: Transcription result or error response
        
    Raises:
        ValueError: If file type is not supported
        Exception: For other transcription errors
    """
    # Validate file type
    if not is_audio_file(file.filename):
        raise ValueError(
            "Invalid file type. Only .mp3, .wav, .m4a, .webm are allowed."
        )
    
    # Send file to Groq Whisper model
    transcription = groq_client.audio.transcriptions.create(
        file=file.file,
        model=settings.DEFAULT_WHISPER_MODEL
    )
    
    # Extract text from response (handle different response formats)
    text = ""
    if hasattr(transcription, 'text'):
        text = transcription.text
    elif isinstance(transcription, dict):
        text = transcription.get("text", transcription.get("transcription", ""))
    
    return {
        "status": "success",
        "model": settings.DEFAULT_WHISPER_MODEL,
        "transcription": text
    }
