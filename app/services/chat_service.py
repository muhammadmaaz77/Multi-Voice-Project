"""
Chat service for conversational AI using Groq Chat API.
"""
from typing import List, Dict, Any
from app.services.groq_client import groq_client
from app.models.chat_models import ChatMessage

async def generate_chat_response(model: str, messages: List[ChatMessage]) -> str:
    """
    Generate AI response using Groq Chat Completions API.
    
    Args:
        model: Groq model name (e.g., "llama3-8b-8192")
        messages: List of chat messages with role and content
        
    Returns:
        str: Generated AI response text
        
    Raises:
        Exception: For API errors or response parsing issues
    """
    # Convert Pydantic models to dict format for Groq API
    message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    # Call Groq Chat Completions API
    response = groq_client.chat.completions.create(
        model=model,
        messages=message_dicts,
        temperature=0.7,
        max_tokens=512
    )
    
    # Extract the assistant's reply
    if hasattr(response, 'choices') and response.choices:
        choice = response.choices[0]
        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
            return choice.message.content
    
    # Fallback for different response formats
    if isinstance(response, dict):
        choices = response.get('choices', [])
        if choices:
            message = choices[0].get('message', {})
            return message.get('content', '')
    
    raise Exception("Unable to extract response from Groq API")

async def transcribe_and_chat(audio_file, model: str = "llama3-8b-8192") -> Dict[str, str]:
    """
    Transcribe audio and generate AI chat response.
    
    Args:
        audio_file: Uploaded audio file
        model: Groq model name for chat completion
        
    Returns:
        dict: Contains transcription and AI reply
        
    Raises:
        Exception: For transcription or chat generation errors
    """
    from app.services.stt_service import transcribe_audio
    
    # Step 1: Transcribe audio
    transcription_result = await transcribe_audio(audio_file)
    if transcription_result["status"] != "success":
        raise Exception(f"Transcription failed: {transcription_result}")
    
    transcribed_text = transcription_result["transcription"]
    
    # Step 2: Generate chat response
    messages = [
        ChatMessage(role="system", content="You are a helpful voice AI assistant."),
        ChatMessage(role="user", content=transcribed_text)
    ]
    
    ai_reply = await generate_chat_response(model, messages)
    
    return {
        "transcription": transcribed_text,
        "reply": ai_reply
    }
