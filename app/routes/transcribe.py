"""
Transcription routes for speech-to-text using Groq Whisper models.
"""
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from app.auth import verify_api_key
from app.services.stt_service import transcribe_audio

router = APIRouter()

@router.post("/transcribe", dependencies=[Depends(verify_api_key)])
async def transcribe(file: UploadFile = File(...)):
    """
    Secured endpoint for audio transcription using Groq Whisper model.
    Accepts audio file upload, returns transcription result.
    """
    try:
        result = await transcribe_audio(file)
        return result
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )
