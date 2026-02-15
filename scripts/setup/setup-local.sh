#!/bin/bash

# Job Hunter AI - Local Development Setup (No Docker)
# For Linux/Mac

set -e

echo "🚀 Job Hunter AI - Setup Local (Sem Docker)"
echo "==========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado. Instale Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if (( $(echo "$PYTHON_VERSION < 3.11" | bc -l) )); then
    echo -e "${RED}❌ Python $PYTHON_VERSION encontrado. Requer Python 3.11+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $(python3 --version)${NC}"

# Check Node.js
echo "📦 Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js não encontrado. Instale Node.js 20+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if (( NODE_VERSION < 20 )); then
    echo -e "${RED}❌ Node.js v$NODE_VERSION encontrado. Requer v20+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node --version)${NC}"

# Check Redis (optional)
echo "🔴 Verificando Redis..."
if command -v redis-server &> /dev/null; then
    echo -e "${GREEN}✅ Redis instalado${NC}"
else
    echo -e "${YELLOW}⚠️  Redis não encontrado (opcional)${NC}"
    echo "   Instale com: sudo apt install redis-server (Ubuntu/Debian)"
    echo "            ou: brew install redis (Mac)"
fi

echo ""
echo "📁 Criando estrutura de diretórios..."
mkdir -p data logs backups

# Backend setup
echo ""
echo "🐍 Configurando Backend Python..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "   Criando virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
echo "   Atualizando pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "   Instalando dependências..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}   ✅ Dependências backend instaladas${NC}"
else
    echo -e "${YELLOW}   ⚠️  requirements.txt não encontrado (será criado na próxima fase)${NC}"
fi

# Copy .env if not exists
if [ ! -f ".env.local" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        echo -e "${GREEN}   ✅ Criado .env.local${NC}"
    fi
fi

cd ..

# Frontend setup
echo ""
echo "📦 Configurando Frontend Node.js..."
cd frontend

# Install dependencies
if [ -f "package.json" ]; then
    echo "   Instalando dependências npm..."
    npm install > /dev/null 2>&1
    echo -e "${GREEN}   ✅ Dependências frontend instaladas${NC}"
else
    echo -e "${YELLOW}   ⚠️  package.json não encontrado (será criado na próxima fase)${NC}"
fi

# Copy .env if not exists
if [ ! -f ".env.local" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        echo -e "${GREEN}   ✅ Criado .env.local${NC}"
    fi
fi

cd ..

echo ""
echo -e "${GREEN}✅ Setup local completo!${NC}"
echo ""
echo "📝 Próximos passos:"
echo ""
echo "1. Configure suas API keys:"
echo "   - backend/.env.local"
echo "   - frontend/.env.local"
echo ""
echo "2. Inicie os serviços:"
echo "   Terminal 1: ./local-start-backend.sh"
echo "   Terminal 2: ./local-start-frontend.sh"
echo ""
echo "3. (Opcional) Inicie Redis:"
echo "   Terminal 3: redis-server"
echo ""
echo "4. Acesse:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
