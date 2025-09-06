# Voice AI Bot Project

This is the main documentation for your production-ready Voice AI Bot. All unnecessary test files, utility scripts, and extra markdown files have been removed for a clean deployment.

## Features
- Multi-language, multi-speaker real-time chat
- Emotion detection
- Session history and analytics
- Modern animated UI (React + Vite)
- FastAPI backend
- Docker and local deployment

## How to Run
1. **Backend**: `python -m uvicorn main:app --reload --port 8001`
2. **Frontend**: `cd frontend && npm install && npm run dev`
3. **Access**: Open `http://localhost:3001` in your browser

## Configuration
- Edit `.env.local` for API keys and backend URLs
- Vite proxy is set to forward `/api` requests to backend on port 8001

## Folder Structure
- `app/` - Backend code
- `frontend/` - React frontend
- `voice_ai.db` - SQLite database
- `Dockerfile` and `docker-compose.yml` for containerization

## Contact
For support or questions, contact the project maintainer.
