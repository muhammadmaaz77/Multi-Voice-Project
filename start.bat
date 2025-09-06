@echo off
REM Voice AI Bot - Quick Start Script for Windows
REM This script sets up and runs the Voice AI Bot with Docker

echo 🎤 Voice AI Bot - Phase 5B Quick Start
echo ======================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Visit: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

echo ✅ Docker is installed

REM Check if .env file exists
if not exist ".env" (
    echo ⚙️  Creating .env file from template...
    copy .env.example .env
    echo 📝 Please edit .env file and add your GROQ_API_KEY
    echo    Then run this script again.
    pause
    exit /b 1
)

echo ✅ Environment file found

REM Start the application
echo 🚀 Starting Voice AI Bot...
docker-compose -f docker-compose.simple.yml up --build -d

echo.
echo 🎉 Voice AI Bot is starting!
echo.
echo 📊 Checking health in 10 seconds...
timeout /t 10 /nobreak > nul

REM Health check
curl -s http://localhost:8000/health > nul 2>&1
if errorlevel 1 (
    echo ⚠️  Service starting... please wait a moment and check http://localhost:8000/health
) else (
    echo ✅ Voice AI Bot is running successfully!
    echo.
    echo 🌐 Access your Voice AI Bot:
    echo    • API: http://localhost:8000
    echo    • Health: http://localhost:8000/health
    echo    • Docs: http://localhost:8000/docs
    echo.
    echo 📋 Quick Commands:
    echo    • View logs: docker-compose logs -f backend
    echo    • Stop: docker-compose down
    echo    • Restart: docker-compose restart
)

echo.
echo 🎯 Your Voice AI Bot is ready for DevOps handoff!
pause
