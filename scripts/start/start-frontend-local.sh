#!/bin/bash

# Start Frontend Server Locally

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules não encontrado. Execute ./setup-local.sh primeiro"
    exit 1
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  Aviso: .env.local não encontrado, usando valores padrão"
fi

echo "🚀 Iniciando Frontend Next.js..."
echo "   URL: http://localhost:3000"
echo "   Para parar: Ctrl+C"
echo ""

# Start development server
npm run dev
