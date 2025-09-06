"""
Phase 4 API routes for enhanced Voice AI features.
Includes speaker identification, emotion detection, and session management.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict
from app.auth import verify_api_key
from app.models.chat_models import ChatMessage
from modules.speaker_id.speaker_service import speaker_identifier
from modules.emotion.emotion_service import emotion_detector
from modules.auth.auth_service import enhanced_auth_service
from app.services.conversation_logger import conversation_logger
from app.services.stt_service import transcribe_audio

router = APIRouter()

@router.post("/session/start", dependencies=[Depends(verify_api_key)])
async def start_session(
    source_language: str = Form(default="auto"),
    target_language: str = Form(default="en"),
    voice_preference: str = Form(default="default")
):
    """
    Start a new conversation session with Phase 4 features.
    """
    try:
        # Create enhanced session
        preferences = {
            "source_language": source_language,
            "target_language": target_language,
            "voice_preference": voice_preference
        }
        
        session_id = enhanced_auth_service.create_session(
            api_key="fast_API_KEY",  # Use actual API key validation
            preferences=preferences
        )
        
        # Start conversation logging
        conversation_logger.start_session(
            session_id, source_language, target_language
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "source_language": source_language,
            "target_language": target_language,
            "voice_preference": voice_preference
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

@router.post("/analyze-text", dependencies=[Depends(verify_api_key)])
async def analyze_text(
    text: str = Form(...),
    session_id: Optional[str] = Form(None)
):
    """
    Analyze text for speaker identification and emotion detection.
    """
    try:
        # Speaker identification
        speaker_id, speaker_confidence = speaker_identifier.identify_speaker(text)
        speaker_info = speaker_identifier.get_speaker_info(speaker_id)
        speaker_label = speaker_info.label if speaker_info else "Unknown"
        
        # Emotion detection
        emotion_result = emotion_detector.detect_emotion(text)
        
        # Log to conversation if session provided
        if session_id:
            conversation_logger.log_conversation(
                session_id=session_id,
                speaker_id=speaker_id,
                speaker_label=speaker_label,
                original_text=text,
                emotion=emotion_result.primary_emotion.value,
                emotion_confidence=emotion_result.confidence
            )
        
        return {
            "status": "success",
            "speaker": {
                "id": speaker_id,
                "label": speaker_label,
                "confidence": speaker_confidence
            },
            "emotion": {
                "primary": emotion_result.primary_emotion.value,
                "confidence": emotion_result.confidence,
                "all_scores": emotion_result.emotion_scores,
                "indicators": emotion_result.detected_indicators
            },
            "text": text
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

@router.post("/voice-analyze", dependencies=[Depends(verify_api_key)])
async def voice_analyze(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """
    Analyze uploaded audio for transcription, speaker ID, and emotion.
    """
    try:
        # Transcribe audio
        transcription_result = await transcribe_audio(file)
        if transcription_result["status"] != "success":
            raise Exception("Transcription failed")
        
        text = transcription_result["transcription"]
        
        # Speaker identification
        speaker_id, speaker_confidence = speaker_identifier.identify_speaker(text)
        speaker_info = speaker_identifier.get_speaker_info(speaker_id)
        speaker_label = speaker_info.label if speaker_info else "Unknown"
        
        # Emotion detection
        emotion_result = emotion_detector.detect_emotion(text)
        
        # Log to conversation if session provided
        if session_id:
            conversation_logger.log_conversation(
                session_id=session_id,
                speaker_id=speaker_id,
                speaker_label=speaker_label,
                original_text=text,
                emotion=emotion_result.primary_emotion.value,
                emotion_confidence=emotion_result.confidence,
                audio_file_path=file.filename
            )
        
        return {
            "status": "success",
            "transcription": text,
            "speaker": {
                "id": speaker_id,
                "label": speaker_label,
                "confidence": speaker_confidence
            },
            "emotion": {
                "primary": emotion_result.primary_emotion.value,
                "confidence": emotion_result.confidence,
                "all_scores": emotion_result.emotion_scores
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

@router.get("/session/{session_id}/history", dependencies=[Depends(verify_api_key)])
async def get_session_history(session_id: str):
    """
    Get conversation history for a session.
    """
    try:
        session = conversation_logger.get_session_history(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "status": "success",
            "session": {
                "session_id": session.session_id,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "source_language": session.source_language,
                "target_language": session.target_language,
                "participant_count": session.participant_count,
                "total_entries": session.total_entries,
                "entries": [
                    {
                        "timestamp": entry.timestamp,
                        "speaker_label": entry.speaker_label,
                        "original_text": entry.original_text,
                        "emotion": entry.emotion,
                        "emotion_confidence": entry.emotion_confidence,
                        "translated_text": entry.translated_text
                    }
                    for entry in session.entries
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

@router.post("/session/{session_id}/end", dependencies=[Depends(verify_api_key)])
async def end_session(session_id: str):
    """
    End a conversation session.
    """
    try:
        success = conversation_logger.end_session(session_id)
        enhanced_auth_service.end_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "status": "success",
            "message": "Session ended successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

@router.get("/sessions/recent", dependencies=[Depends(verify_api_key)])
async def get_recent_sessions():
    """
    Get list of recent sessions.
    """
    try:
        recent_sessions = conversation_logger.get_recent_sessions(10)
        
        sessions_info = []
        for session_id in recent_sessions:
            session = conversation_logger.get_session_history(session_id)
            if session:
                sessions_info.append({
                    "session_id": session_id,
                    "start_time": session.start_time,
                    "total_entries": session.total_entries,
                    "participant_count": session.participant_count,
                    "languages": f"{session.source_language} → {session.target_language}"
                })
        
        return {
            "status": "success",
            "sessions": sessions_info
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

@router.get("/system/status", dependencies=[Depends(verify_api_key)])
async def get_system_status():
    """
    Get system status and statistics.
    """
    try:
        # Get authentication stats
        active_sessions = enhanced_auth_service.get_active_sessions_count()
        
        # Get speaker stats
        all_speakers = speaker_identifier.get_all_speakers()
        
        return {
            "status": "success",
            "system": {
                "active_sessions": active_sessions,
                "identified_speakers": len(all_speakers),
                "phase": "Phase 4 - Enhanced Features",
                "features": [
                    "Speaker Identification",
                    "Emotion Detection", 
                    "Session Management",
                    "Conversation Logging",
                    "Enhanced Authentication"
                ]
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )
