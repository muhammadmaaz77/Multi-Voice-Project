
"""
Chat routes for LLM interactions using Groq API.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.auth import verify_api_key
from app.models.chat_models import ChatTestRequest, ChatRequest
from app.services.groq_client import groq_client
from app.services.chat_service import generate_chat_response, transcribe_and_chat

router = APIRouter()

@router.post("/chat-test", dependencies=[Depends(verify_api_key)])
async def chat_test(request: ChatTestRequest):
    """
    Secured endpoint to test Groq chat completion.
    Accepts model and message, returns Groq raw response.
    """
    try:
        groq_response = groq_client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.message}]
        )
        return groq_response
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"status": "error", "detail": str(e)}
        )

@router.post("/chat", dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest):
    """
    Secured endpoint for conversational AI using Groq Chat API.
    Accepts model and messages, returns AI-generated reply.
    """
    try:
        ai_reply = await generate_chat_response(request.model, request.messages)
        return {
            "status": "success",
            "model": request.model,
            "reply": ai_reply
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

@router.post("/transcribe-and-chat", dependencies=[Depends(verify_api_key)])
async def transcribe_and_chat_endpoint(
    file: UploadFile = File(...),
    model: str = Form(default="llama3-8b-8192")
):
    """
    Secured endpoint that combines transcription and chat.
    Transcribes audio file and generates AI response.
    """
    try:
        result = await transcribe_and_chat(file, model)
        return {
            "status": "success",
            "transcription": result["transcription"],
            "reply": result["reply"]
        }
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
