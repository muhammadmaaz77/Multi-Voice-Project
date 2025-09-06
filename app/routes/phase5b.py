"""
Phase 5B Routes - Multiparty, Persistent Memory, and Local Mode
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

try:
    from sqlalchemy.orm import Session
    from app.db import get_db, DatabaseService
    from app.auth import verify_api_key, verify_admin_key
    HAS_DATABASE = True
except ImportError:
    Session = None
    get_db = lambda: None
    DatabaseService = None
    verify_api_key = lambda: None
    verify_admin_key = lambda: None
    HAS_DATABASE = False

from app.services.multiparty import multiparty_manager
from app.services.persistent_memory import persistent_memory_service
from app.services.local_mode import local_mode_service

router = APIRouter()

# Pydantic models
class CreateSessionRequest(BaseModel):
    session_id: str
    user_id: str
    max_participants: int = 4
    participants: List[Dict[str, Any]] = []

class JoinSessionRequest(BaseModel):
    session_id: str
    speaker_id: str
    participant_info: Dict[str, Any]

class SessionSummaryRequest(BaseModel):
    session_id: str
    participants: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]

class LocalModeRequest(BaseModel):
    asr_mode: Optional[str] = None
    tts_mode: Optional[str] = None

class ProcessAudioRequest(BaseModel):
    audio_data: str  # Base64 encoded
    language: str = "en"
    processing_mode: Optional[str] = None

# Multiparty Session Endpoints

@router.post("/sessions/multiparty")
async def create_multiparty_session(
    request: CreateSessionRequest,
    db = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new multiparty conversation session"""
    try:
        # Create session in multiparty manager
        session = multiparty_manager.create_session(
            request.session_id, 
            request.max_participants
        )
        
        # Store in persistent memory
        if request.participants:
            persistent_memory_service.store_conversation_context(
                db, request.session_id, request.user_id, request.participants
            )
        
        return {
            "status": "created",
            "session_id": request.session_id,
            "max_participants": request.max_participants,
            "current_participants": 0,
            "created_at": session.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/sessions/multiparty/{session_id}")
async def get_multiparty_session_info(
    session_id: str,
    db = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get information about a multiparty session"""
    session_info = multiparty_manager.get_session_info(session_id)
    
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get persistent summary if available
    summary = persistent_memory_service.get_session_summary(db, session_id)
    if summary:
        session_info["summary"] = summary
    
    return session_info

@router.get("/sessions/multiparty")
async def list_multiparty_sessions(
    api_key: str = Depends(verify_api_key)
):
    """List all active multiparty sessions"""
    sessions = multiparty_manager.get_all_sessions()
    
    return {
        "active_sessions": len(sessions),
        "sessions": sessions,
        "total_participants": sum(s.get("participant_count", 0) for s in sessions)
    }

# Persistent Memory Endpoints

@router.post("/memory/session-summary")
async def store_session_summary(
    request: SessionSummaryRequest,
    db = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Store a session summary in persistent memory"""
    try:
        success = persistent_memory_service.store_session_summary(
            db, request.session_id, request.participants, request.messages
        )
        
        if success:
            return {
                "status": "stored",
                "session_id": request.session_id,
                "message_count": len(request.messages),
                "participant_count": len(request.participants)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store session summary")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing summary: {str(e)}")

@router.get("/memory/session-summary/{session_id}")
async def get_session_summary(
    session_id: str,
    db = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get session summary from persistent memory"""
    summary = persistent_memory_service.get_session_summary(db, session_id)
    
    if summary:
        return {
            "session_id": session_id,
            "summary": summary,
            "retrieved_at": persistent_memory_service._calculate_duration([])
        }
    else:
        raise HTTPException(status_code=404, detail="Session summary not found")

@router.get("/memory/user/{user_id}/last-session")
async def get_user_last_session(
    user_id: str,
    db = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get user's last session summary for context"""
    last_session = persistent_memory_service.get_user_last_session_summary(db, user_id)
    
    if last_session:
        return last_session
    else:
        return {
            "message": "No previous session found for user",
            "user_id": user_id
        }

@router.get("/memory/analytics/{session_id}")
async def get_session_analytics(
    session_id: str,
    db = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get analytics for a session"""
    analytics = persistent_memory_service.get_session_analytics(db, session_id)
    return analytics

# Local Mode Endpoints

@router.get("/local-mode/status")
async def get_local_mode_status(
    api_key: str = Depends(verify_api_key)
):
    """Get current local mode status"""
    return local_mode_service.get_status()

@router.post("/local-mode/configure")
async def configure_local_mode(
    request: LocalModeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Configure local/cloud processing modes"""
    results = {}
    
    if request.asr_mode:
        results["asr_mode_set"] = local_mode_service.set_asr_mode(request.asr_mode)
    
    if request.tts_mode:
        results["tts_mode_set"] = local_mode_service.set_tts_mode(request.tts_mode)
    
    # Return current status
    results["current_status"] = local_mode_service.get_status()
    
    return results

@router.post("/local-mode/process-audio")
async def process_audio_local_mode(
    request: ProcessAudioRequest,
    api_key: str = Depends(verify_api_key)
):
    """Process audio using current local/cloud mode"""
    try:
        import base64
        
        # Decode base64 audio data
        audio_data = base64.b64decode(request.audio_data)
        
        # Process using current mode
        result = local_mode_service.process_audio_transcription(
            audio_data, request.language
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

@router.post("/local-mode/generate-speech")
async def generate_speech_local_mode(
    text: str = Query(..., description="Text to convert to speech"),
    voice_id: str = Query("default", description="Voice ID to use"),
    language: str = Query("en", description="Language code"),
    api_key: str = Depends(verify_api_key)
):
    """Generate speech using current local/cloud mode"""
    try:
        result = local_mode_service.generate_speech(text, voice_id, language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech generation failed: {str(e)}")

@router.post("/local-mode/switch-fallback/{service}")
async def switch_to_fallback_mode(
    service: str,
    api_key: str = Depends(verify_api_key)
):
    """Switch to fallback mode for a service (asr or tts)"""
    if service not in ["asr", "tts"]:
        raise HTTPException(status_code=400, detail="Service must be 'asr' or 'tts'")
    
    success = local_mode_service.switch_to_fallback_mode(service)
    
    if success:
        return {
            "status": "switched",
            "service": service,
            "new_status": local_mode_service.get_status()
        }
    else:
        raise HTTPException(status_code=500, detail=f"Failed to switch {service} to fallback mode")

# Health check for Phase 5B features
@router.get("/phase5b/health")
async def phase5b_health_check():
    """Health check for Phase 5B features"""
    return {
        "phase": "5B",
        "status": "operational",
        "features": {
            "multiparty_sessions": "available",
            "persistent_memory": "available" if HAS_DATABASE else "mock_mode",
            "local_mode": "available",
            "database": "connected" if HAS_DATABASE else "disabled"
        },
        "active_sessions": len(multiparty_manager.get_all_sessions()),
        "local_mode_status": local_mode_service.get_status()
    }
