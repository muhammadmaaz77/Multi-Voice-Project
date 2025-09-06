"""
Pydantic models for speech-to-text requests and responses.
"""
from pydantic import BaseModel

class TranscriptionResponse(BaseModel):
    """Response model for transcription endpoints."""
    status: str
    model: str
    transcription: str

class TranscriptionError(BaseModel):
    """Error response model for transcription endpoints."""
    status: str
    detail: str
