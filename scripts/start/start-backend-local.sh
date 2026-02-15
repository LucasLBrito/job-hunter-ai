#!/bin/bash

# Start Backend Server Locally

cd backend

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment não encontrado. Execute ./setup-local.sh primeiro"
    exit 1
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  Aviso: .env.local não encontrado, usando valores padrão"
fi

echo "🚀 Iniciando Backend FastAPI..."
echo "   URL: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Para parar: Ctrl+C"
echo ""

# Start with reload for development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --env-file .env.local
