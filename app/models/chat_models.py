"""
Pydantic models for chat-related requests and responses.
"""
from pydantic import BaseModel
from typing import List, Dict, Any

class ChatTestRequest(BaseModel):
    """Request model for chat test endpoint."""
    model: str
    message: str

class ChatMessage(BaseModel):
    """Model for individual chat messages."""
    role: str  # "system", "user", or "assistant"
    content: str

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    model: str
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    """Response model for chat endpoints."""
    status: str
    model: str
    reply: str

class TranscribeAndChatResponse(BaseModel):
    """Response model for transcribe-and-chat endpoint."""
    status: str
    transcription: str
    reply: str
