#!/bin/bash

# Voice AI Bot - Quick Start Script
# This script sets up and runs the Voice AI Bot with Docker

echo "🎤 Voice AI Bot - Phase 5B Quick Start"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✅ Docker and docker-compose are installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your GROQ_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

echo "✅ Environment file found"

# Check if GROQ_API_KEY is set
source .env
if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your_groq_api_key_here" ]; then
    echo "❌ GROQ_API_KEY not set in .env file"
    echo "   Please edit .env and add your API key"
    exit 1
fi

echo "✅ API keys configured"

# Start the application
echo "🚀 Starting Voice AI Bot..."
docker-compose -f docker-compose.simple.yml up --build -d

echo ""
echo "🎉 Voice AI Bot is starting!"
echo ""
echo "📊 Checking health..."
sleep 10

# Health check
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Voice AI Bot is running successfully!"
    echo ""
    echo "🌐 Access your Voice AI Bot:"
    echo "   • API: http://localhost:8000"
    echo "   • Health: http://localhost:8000/health"
    echo "   • Docs: http://localhost:8000/docs"
    echo ""
    echo "📋 Quick Commands:"
    echo "   • View logs: docker-compose logs -f backend"
    echo "   • Stop: docker-compose down"
    echo "   • Restart: docker-compose restart"
else
    echo "⚠️  Service starting... please wait a moment and check http://localhost:8000/health"
fi

echo ""
echo "🎯 Your Voice AI Bot is ready for DevOps handoff!"
