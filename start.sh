#!/bin/bash

# PDF Document Search System - Startup Script

echo "🚀 Starting PDF Document Search System..."

# Check if Docker and Docker Compose are available
if command -v docker-compose &> /dev/null; then
    echo "📦 Using Docker Compose..."
    docker-compose up --build
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "📦 Using Docker Compose (v2)..."
    docker compose up --build
else
    echo "⚠️  Docker Compose not found. Starting services manually..."
    echo "📋 Please ensure Python 3.11+ is installed."
    
    # Start vector store in background
    echo "🔗 Starting Vector Store service..."
    cd vector-store
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8001 &
    VECTOR_PID=$!
    cd ..
    
    # Wait a moment for vector store to start
    sleep 5
    
    # Start API backend
    echo "🌐 Starting API Backend service..."
    cd api-backend
    pip install -r requirements.txt
    export VECTOR_STORE_URL=http://localhost:8001
    uvicorn main:app --host 0.0.0.0 --port 8000 &
    API_PID=$!
    cd ..
    
    echo "✅ Services started!"
    echo "   - API Backend: http://localhost:8000"
    echo "   - Vector Store: http://localhost:8001"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "📝 To stop services manually:"
    echo "   kill $VECTOR_PID $API_PID"
    
    # Wait for interrupt
    trap "echo '🛑 Stopping services...'; kill $VECTOR_PID $API_PID; exit" INT
    wait
fi

# tests
cd /Users/venkateshtadinada/Documents/VS-Code-Projects/p3-search/tests && python test.py