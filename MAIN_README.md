# Voice AI Bot - Multi-Language Real-Time Communication System

A production-ready Voice AI Bot with multi-language support, real-time translation, emotion detection, and modern UI.

## 🚀 Features

- **Multi-Language Support**: Real-time translation between languages
- **Voice Recording**: High-quality audio capture and processing  
- **Emotion Detection**: AI-powered sentiment analysis
- **Session History**: Persistent chat storage with SQLite
- **Modern UI**: React + Vite with animated components
- **WebSocket Support**: Real-time communication
- **Analytics Dashboard**: Usage tracking and insights
- **Docker Ready**: Containerized deployment

## 📁 Project Structure

```
Multi Voice/
├── app/                    # Backend application
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   ├── models/            # Data models
│   └── db/               # Database setup
├── frontend/              # React frontend
│   ├── src/              # Source code
│   └── public/           # Static assets
├── modules/              # Shared modules
├── main.py              # Backend entry point
├── requirements.txt     # Python dependencies
└── docker-compose.yml  # Container orchestration
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- GROQ API Key

### 1. Setup Environment
```bash
# Clone/navigate to project
cd "Multi Voice"

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install Python dependencies
pip install -r requirements.txt

# Setup frontend
cd frontend
npm install
cd ..
```

### 2. Configuration
Create `.env` file in root directory:
```
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./voice_ai.db
```

Create `frontend/.env.local`:
```
VITE_API_URL=http://localhost:8001
VITE_WS_URL=ws://localhost:8001
```

### 3. Run Application
```bash
# Terminal 1: Start Backend
python -m uvicorn main:app --reload --port 8001

# Terminal 2: Start Frontend  
cd frontend
npm run dev
```

### 4. Access Application
- Frontend: http://localhost:3001
- API Docs: http://localhost:8001/docs
- Admin Dashboard: http://localhost:8001/admin

## 🎯 Usage

1. **Open Application**: Navigate to http://localhost:3001
2. **Select Language**: Choose your preferred language
3. **Join Room**: Enter a room name to start chatting
4. **Record Voice**: Click record button to capture audio
5. **Real-Time Translation**: Messages are automatically translated for other users

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access application
open http://localhost:3001
```

## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /chat` - Send chat message
- `POST /transcribe` - Audio transcription
- `WS /api/v2/ws/multi-language/{room_id}` - WebSocket for real-time chat
- `GET /api/v1/analytics/overview` - Analytics data

## 🌍 Supported Languages

- English (en)
- Spanish (es) 
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Dutch (nl)
- Russian (ru)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the console logs for errors
3. Ensure all environment variables are set
4. Verify GROQ API key is valid

---

Built with ❤️ using FastAPI, React, and modern web technologies.
