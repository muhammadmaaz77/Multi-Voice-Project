"""
main.py - Voice AI Bot Backend Entry Point (Phase 5B)
FastAPI application with multiparty conversations, persistent memory, and containerization.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import base, chat, transcribe, ws_stream_simple as ws_stream, voice_profiles, analytics, dashboard, phase5b, multi_lang_simple
from app.db import create_tables

# Initialize FastAPI application
app = FastAPI(
    title="Voice AI Bot Backend - Phase 5B",
    description="Multi-Voice AI System with Multiparty Conversations, Persistent Memory, and Local Mode",
    version="5.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(base.router, tags=["Base"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(transcribe.router, tags=["Transcription"])

# Phase 5A routers
app.include_router(ws_stream.router, prefix="/api/v1", tags=["WebSocket Streaming"])
app.include_router(voice_profiles.router, prefix="/api/v1", tags=["Voice Profiles"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(dashboard.router, prefix="/admin", tags=["Dashboard"])

# Phase 5B routers
app.include_router(phase5b.router, prefix="/api/v2", tags=["Phase 5B - Multiparty & Persistence"])
app.include_router(multi_lang_simple.router, prefix="/api/v2", tags=["Multi-Language Simple"])

# To run: uvicorn main:app --reload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
