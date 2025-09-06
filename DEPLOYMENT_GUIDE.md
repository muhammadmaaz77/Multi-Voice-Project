# 🚀 Voice AI Bot - Phase 5B Deployment Guide

## 📋 Quick Start (3 Commands)

```bash
# 1. Set your API keys
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# 2. Start with Docker
docker-compose -f docker-compose.simple.yml up --build

# 3. Test the API
curl http://localhost:8000/health
```

**That's it!** Your Voice AI Bot is now running at http://localhost:8000

## 🎯 Phase 5B Features

✅ **Multiparty Conversations** - Up to 4 speakers simultaneously  
✅ **Persistent Memory** - Session summaries stored in database  
✅ **Local Mode Toggle** - Switch between cloud/local ASR/TTS  
✅ **Containerized** - One command deployment  

## 🐳 Docker Options

### Option 1: Simple (SQLite, Single Container)
```bash
docker-compose -f docker-compose.simple.yml up --build
```
- Uses SQLite database (no external DB needed)
- Perfect for development and testing
- Single container, easy to deploy

### Option 2: Production (PostgreSQL + Redis)
```bash
docker-compose up --build
```
- Uses PostgreSQL database
- Includes Redis for caching
- Ready for production scaling

## 🔧 Configuration

### Required Environment Variables
```bash
# .env file
GROQ_API_KEY=your_groq_api_key_here
ADMIN_KEY=your_secure_admin_key
```

### Optional Settings
```bash
LOCAL_MODE=false              # Use cloud APIs (true for local mode)
ENABLE_MULTIPARTY=true        # Enable multiparty sessions
MAX_SPEAKERS=4                # Maximum speakers per session
```

## 🌐 API Endpoints

### Basic
- `GET /` - Welcome page
- `GET /health` - Health check
- `POST /chat` - Text chat with AI

### Multiparty (Phase 5B)
- `POST /api/v2/multiparty/sessions` - Create multiparty session
- `POST /api/v2/multiparty/sessions/{id}/join` - Join session
- `GET /api/v2/multiparty/sessions/{id}/speakers` - List speakers

### Memory (Phase 5B)
- `GET /api/v2/memory/summary/{session_id}` - Get session summary
- `POST /api/v2/memory/retain/{session_id}` - Save important session

### Local Mode (Phase 5B)
- `POST /api/v2/local-mode/toggle` - Switch cloud/local mode
- `GET /api/v2/local-mode/status` - Check current mode

## 🧪 Testing

### Test Multiparty Session
```bash
# Create session
curl -X POST http://localhost:8000/api/v2/multiparty/sessions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin123" \
  -d '{"max_speakers": 3, "session_name": "Test Session"}'

# Join session (replace session_id)
curl -X POST http://localhost:8000/api/v2/multiparty/sessions/SESSION_ID/join \
  -H "Content-Type: application/json" \
  -d '{"speaker_id": "speaker1", "user_name": "John"}'
```

### Test WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/session_123');
ws.onmessage = (event) => {
  console.log('AI Response:', JSON.parse(event.data));
};
```

## 🚀 VPS Deployment

### 1. Server Setup
```bash
# On your VPS (Ubuntu/Debian)
sudo apt update
sudo apt install docker.io docker-compose git

# Clone project
git clone <your-repo> voice-ai-bot
cd voice-ai-bot
```

### 2. Configure Environment
```bash
# Set your API keys
cp .env.example .env
nano .env  # Add your GROQ_API_KEY and ADMIN_KEY
```

### 3. Deploy
```bash
# Start the application
docker-compose -f docker-compose.simple.yml up -d

# Check logs
docker-compose logs -f backend

# Your API is now live at http://YOUR_VPS_IP:8000
```

### 4. Domain Setup (Optional)
```bash
# Install nginx
sudo apt install nginx certbot python3-certbot-nginx

# Configure domain
sudo nano /etc/nginx/sites-available/voice-ai-bot

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

## 🐋 Docker Hub Deployment

### 1. Build and Push
```bash
# Build image
docker build -t yourusername/voice-ai-bot:latest .

# Push to Docker Hub
docker push yourusername/voice-ai-bot:latest
```

### 2. Deploy from Docker Hub
```bash
# On any server
docker run -d \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e ADMIN_KEY=admin123 \
  yourusername/voice-ai-bot:latest
```

## 🔍 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using port 8000
netstat -tulpn | grep :8000

# Kill the process
sudo kill -9 <process_id>
```

**Docker not starting:**
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker
sudo systemctl start docker
```

**Permission denied:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

### Health Check
```bash
# Check if everything is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "..."}
```

## 📊 Monitoring

### View Logs
```bash
# Real-time logs
docker-compose logs -f backend

# Specific service logs
docker logs voice_ai_backend
```

### Resource Usage
```bash
# Container stats
docker stats

# System resources
docker system df
```

## 🎯 Next Steps for DevOps

This containerized setup is ready for:

1. **Kubernetes deployment** - Use the Docker images
2. **Load balancing** - Scale the backend containers
3. **CI/CD pipelines** - Automated deployments
4. **Monitoring** - Add Prometheus/Grafana
5. **Backup** - Database backup strategies

## 🛡️ Security Notes

- Change default ADMIN_KEY in production
- Use HTTPS with SSL certificates
- Implement API rate limiting
- Regular security updates

---

**🎉 Your Voice AI Bot is now containerized and ready for production!**
