"""
Voice profile management routes for Phase 5A
REST API endpoints for voice cloning pipeline.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import json

from ..auth import verify_api_key
from ..services.voice.voice_profile_service import voice_profile_manager

router = APIRouter()

@router.post("/voice/profiles")
async def create_voice_profile(
    name: str = Form(...),
    language: str = Form("en"),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new voice profile for cloning.
    
    - **name**: Display name for the voice profile
    - **language**: Language code (default: en)
    """
    try:
        profile_id = await voice_profile_manager.create_voice_profile(
            user_id=api_key,  # Using API key as user ID for Phase 5A
            name=name,
            language=language
        )
        
        return {
            "success": True,
            "profile_id": profile_id,
            "message": "Voice profile created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating voice profile: {str(e)}")

@router.get("/voice/profiles")
async def get_voice_profiles(api_key: str = Depends(verify_api_key)):
    """
    Get all voice profiles for the authenticated user.
    """
    try:
        profiles = voice_profile_manager.get_user_profiles(user_id=api_key)
        
        return {
            "success": True,
            "profiles": [
                {
                    "profile_id": profile.profile_id,
                    "name": profile.name,
                    "language": profile.language,
                    "status": profile.status,
                    "created_at": profile.created_at,
                    "updated_at": profile.updated_at,
                    "sample_count": len(profile.sample_files),
                    "training_progress": profile.training_progress
                }
                for profile in profiles
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving voice profiles: {str(e)}")

@router.get("/voice/profiles/{profile_id}")
async def get_voice_profile(
    profile_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get detailed information about a specific voice profile.
    """
    try:
        profile = voice_profile_manager.get_voice_profile(profile_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        
        # Verify ownership
        if profile.user_id != api_key:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get samples
        samples = voice_profile_manager.get_profile_samples(profile_id)
        
        return {
            "success": True,
            "profile": {
                "profile_id": profile.profile_id,
                "name": profile.name,
                "language": profile.language,
                "status": profile.status,
                "created_at": profile.created_at,
                "updated_at": profile.updated_at,
                "training_progress": profile.training_progress,
                "model_path": profile.model_path,
                "metadata": profile.metadata,
                "samples": [
                    {
                        "sample_id": sample.sample_id,
                        "filename": sample.filename,
                        "duration_seconds": sample.duration_seconds,
                        "quality_score": sample.quality_score,
                        "uploaded_at": sample.uploaded_at
                    }
                    for sample in samples
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving voice profile: {str(e)}")

@router.post("/voice/profiles/{profile_id}/samples")
async def upload_voice_sample(
    profile_id: str,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Upload a voice sample for training.
    
    - **audio_file**: Audio file (WAV, MP3, FLAC, M4A)
    - Audio should be 30-300 seconds long
    - Clear speech, minimal background noise
    """
    try:
        # Verify profile exists and ownership
        profile = voice_profile_manager.get_voice_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        
        if profile.user_id != api_key:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if profile is in a state that allows new samples
        if profile.status in ["processing"]:
            raise HTTPException(
                status_code=400, 
                detail="Cannot upload samples while profile is being processed"
            )
        
        # Read file content
        file_content = await audio_file.read()
        
        # Upload and process sample
        result = await voice_profile_manager.upload_voice_sample(
            profile_id=profile_id,
            file_content=file_content,
            filename=audio_file.filename
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "sample_id": result["sample_id"],
            "quality_score": result["quality_score"],
            "duration": result["duration"],
            "total_samples": result["total_samples"],
            "message": "Voice sample uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading voice sample: {str(e)}")

@router.get("/voice/profiles/{profile_id}/status")
async def get_training_status(
    profile_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get training status for a voice profile.
    """
    try:
        # Verify profile exists and ownership
        profile = voice_profile_manager.get_voice_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        
        if profile.user_id != api_key:
            raise HTTPException(status_code=403, detail="Access denied")
        
        status = voice_profile_manager.get_training_status(profile_id)
        
        return {
            "success": True,
            "status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving training status: {str(e)}")

@router.delete("/voice/profiles/{profile_id}")
async def delete_voice_profile(
    profile_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a voice profile and all associated data.
    """
    try:
        success = await voice_profile_manager.delete_voice_profile(
            profile_id=profile_id,
            user_id=api_key
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Voice profile not found or access denied")
        
        return {
            "success": True,
            "message": "Voice profile deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting voice profile: {str(e)}")

@router.get("/voice/profiles/{profile_id}/samples/{sample_id}")
async def get_voice_sample_info(
    profile_id: str,
    sample_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get information about a specific voice sample.
    """
    try:
        # Verify profile exists and ownership
        profile = voice_profile_manager.get_voice_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        
        if profile.user_id != api_key:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Find sample
        sample = voice_profile_manager.samples.get(sample_id)
        if not sample or sample.profile_id != profile_id:
            raise HTTPException(status_code=404, detail="Voice sample not found")
        
        return {
            "success": True,
            "sample": {
                "sample_id": sample.sample_id,
                "profile_id": sample.profile_id,
                "filename": sample.filename,
                "duration_seconds": sample.duration_seconds,
                "sample_rate": sample.sample_rate,
                "quality_score": sample.quality_score,
                "uploaded_at": sample.uploaded_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sample info: {str(e)}")

@router.post("/voice/profiles/{profile_id}/synthesize")
async def synthesize_voice(
    profile_id: str,
    text: str = Form(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Synthesize speech using a trained voice profile.
    
    - **text**: Text to synthesize
    """
    try:
        # Verify profile exists and ownership
        profile = voice_profile_manager.get_voice_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        
        if profile.user_id != api_key:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if profile is ready
        if profile.status != "ready":
            raise HTTPException(
                status_code=400, 
                detail=f"Voice profile not ready for synthesis. Status: {profile.status}"
            )
        
        # For Phase 5A, return a stub response
        # In Phase 5B, this would integrate with actual TTS synthesis
        return {
            "success": True,
            "message": "Voice synthesis requested",
            "profile_id": profile_id,
            "text": text,
            "status": "queued",
            "estimated_duration": len(text) * 0.05,  # Rough estimate
            "note": "Synthesis integration pending Phase 5B implementation"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error synthesizing voice: {str(e)}")

# Health check endpoint
@router.get("/voice/health")
async def voice_service_health():
    """Voice service health check."""
    return {
        "service": "voice_profiles",
        "status": "healthy",
        "total_profiles": len(voice_profile_manager.profiles),
        "total_samples": len(voice_profile_manager.samples)
    }
