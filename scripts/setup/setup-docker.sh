#!/bin/bash

# Job Hunter AI - Setup Script
# This script sets up the development environment

set -e

echo "🚀 Job Hunter AI - Setup Script"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale Docker primeiro:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instale Docker Compose primeiro:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker e Docker Compose encontrados"
echo ""

# Create necessary directories
echo "📁 Criando diretórios..."
mkdir -p data logs backups
echo "✅ Diretórios criados"
echo ""

# Copy environment files if they don't exist
echo "📝 Configurando arquivos de ambiente..."

if [ ! -f backend/.env.dev ]; then
    cp backend/.env.example backend/.env.dev
    echo "✅ Criado backend/.env.dev"
else
    echo "ℹ️  backend/.env.dev já existe (mantendo)"
fi

if [ ! -f frontend/.env.dev ]; then
    cp frontend/.env.example frontend/.env.dev
    echo "✅ Criado frontend/.env.dev"
else
    echo "ℹ️  frontend/.env.dev já existe (mantendo)"
fi

echo ""
echo "⚠️  IMPORTANTE: Configure suas API keys nos arquivos .env.dev!"
echo ""
echo "   Edite os seguintes arquivos:"
echo "   - backend/.env.dev  (OpenAI/Anthropic, Azure, WhatsApp)"
echo "   - frontend/.env.dev (URL da API)"
echo ""

# Ask if user wants to start services
read -p "Deseja iniciar os serviços agora? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🐳 Iniciando serviços Docker..."
    
    if command -v docker compose &> /dev/null; then
        docker compose -f docker-compose.dev.yml up -d --build
    else
        docker-compose -f docker-compose.dev.yml up -d --build
    fi
    
    echo ""
    echo "✅ Serviços iniciados!"
    echo ""
    echo "📊 Acesse:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📝 Ver logs:"
    echo "   make logs"
    echo ""
    echo "🛑 Parar serviços:"
    echo "   make stop"
else
    echo ""
    echo "Para iniciar os serviços manualmente, execute:"
    echo "   make dev"
fi

echo ""
echo "🎉 Setup completo!"
echo ""
echo "📚 Comandos úteis:"
echo "   make help   - Ver todos os comandos disponíveis"
echo "   make dev    - Iniciar ambiente de desenvolvimento"
echo "   make logs   - Ver logs dos serviços"
echo "   make test   - Rodar testes"
echo "   make stop   - Parar todos os serviços"
echo ""
