# Job Hunter AI - Local Development (No Docker)

## 🚀 Quick Start - Desenvolvimento Local

### Pré-requisitos

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **Redis** (opcional) - Ver [Instalação Redis](#instalação-redis)
- **Git** - [Download](https://git-scm.com/)

---

## 📦 Instalação

### Windows

```bash
# 1. Clone o repositório
git clone <repo-url>
cd job-hunter-ai

# 2. Execute o setup
setup-local.bat
```

### Linux / Mac

```bash
# 1. Clone o repositório
git clone <repo-url>
cd job-hunter-ai

# 2. Torne os scripts executáveis
chmod +x setup-local.sh local-start-*.sh

# 3. Execute o setup
./setup-local.sh
```

---

## ⚙️ Configuração

### 1. Backend (.env.local)

Edite `backend/.env.local`:

```bash
# LLM (escolha um)
OPENAI_API_KEY=sk-your-openai-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key

# WhatsApp Business API
WHATSAPP_API_TOKEN=your-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-id

# Database
DATABASE_URL=sqlite:///./data/database.db

# Redis (se rodando localmente)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-min-256-bits
```

### 2. Frontend (.env.local)

Edite `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🎮 Rodando a Aplicação

### Opção 1: Scripts Automatizados (Recomendado)

**Windows:**
```bash
# Terminal 1 - Backend
local-start-backend.bat

# Terminal 2 - Frontend
local-start-frontend.bat

# Terminal 3 - Redis (opcional)
redis-server
```

**Linux/Mac:**
```bash
# Terminal 1 - Backend
./local-start-backend.sh

# Terminal 2 - Frontend
./local-start-frontend.sh

# Terminal 3 - Redis (opcional)
redis-server
```

### Opção 2: Manual

**Backend:**
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate.bat  # Windows

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

---

## 🌐 URLs de Acesso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

---

## 🛠️ Comandos Úteis

### Backend

```bash
# Ativar ambiente virtual
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat # Windows

# Instalar nova dependência
pip install <package>
pip freeze > requirements.txt

# Rodar migrations
alembic upgrade head

# Criar nova migration
alembic revision --autogenerate -m "description"

# Rodar testes
pytest
pytest --cov=app

# Formatar código
black app/
ruff check app/ --fix

# Type checking
mypy app/

# Criar superuser
python -m app.scripts.create_superuser
```

### Frontend

```bash
cd frontend

# Instalar nova dependência
npm install <package>

# Build para produção
npm run build

# Rodar build de produção
npm run start

# Lint
npm run lint

# Type checking
npm run type-check
```

---

## 🔴 Instalação Redis

### Windows

1. **Download**: https://github.com/microsoftarchive/redis/releases
2. Extrair e executar `redis-server.exe`

**Ou via Chocolatey:**
```bash
choco install redis-64
redis-server
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### Mac

```bash
brew install redis
brew services start redis
```

### Verificar Redis

```bash
redis-cli ping
# Deve retornar: PONG
```

---

## 🐛 Troubleshooting

### Problema: Porta 8000 já em uso

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Problema: Porta 3000 já em uso

```bash
# Usar outra porta
cd frontend
PORT=3001 npm run dev  # Linux/Mac
set PORT=3001 && npm run dev  # Windows
```

### Problema: Virtual environment não ativa

**Windows:**
```bash
# Habilitar execução de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac:**
```bash
# Recriar venv
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Problema: ModuleNotFoundError

```bash
# Reinstalar dependências
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Problema: npm install falha

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📊 Estrutura de Diretórios

```
job-hunter-ai/
├── backend/
│   ├── venv/                  # Virtual environment Python
│   ├── app/                   # Código da aplicação
│   ├── requirements.txt       # Dependências Python
│   └── .env.local             # Variáveis de ambiente
├── frontend/
│   ├── node_modules/          # Dependências Node
│   ├── app/                   # Código Next.js
│   ├── package.json           # Dependências
│   └── .env.local             # Variáveis de ambiente
├── data/                      # SQLite database
├── logs/                      # Application logs
├── setup-local.sh             # Setup Linux/Mac
├── setup-local.bat            # Setup Windows
├── local-start-backend.sh     # Start backend Linux/Mac
├── local-start-backend.bat    # Start backend Windows
├── local-start-frontend.sh    # Start frontend Linux/Mac
└── local-start-frontend.bat   # Start frontend Windows
```

---

## 🔍 Verificação de Saúde

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Redis
redis-cli ping
```

---

## 🚀 Performance Tips

### Backend

1. **Use Redis para cache** - Melhora significativa em scraping
2. **Configure workers** - Para produção local:
   ```bash
   uvicorn app.main:app --workers 4
   ```

### Frontend

1. **Build otimizado** - Use `npm run build` antes de testar performance
2. **Cache de imagens** - Next.js otimiza automaticamente

---

## 🔄 Sincronização com Docker

Você pode alternar entre Docker e local:

```bash
# Local → Docker
docker-compose -f docker-compose.dev.yml up -d

# Docker → Local
docker-compose -f docker-compose.dev.yml down
./setup-local.sh  # Se ainda não configurou
./local-start-backend.sh  # Terminal 1
./local-start-frontend.sh # Terminal 2
```

**Nota**: O banco SQLite (`data/database.db`) é compartilhado entre ambos!

---

## 📚 Próximos Passos

1. ✅ Setup local completo
2. ✅ Serviços rodando
3. [ ] Implementar backend (Fase 2)
4. [ ] Implementar frontend (Fase 9)
5. [ ] Testes
6. [ ] Production deploy

---

## 🆘 Suporte

- **Docker Setup**: Ver [DOCKER_README.md](DOCKER_README.md)
- **Geral**: Ver [README.md](README.md)
- **Issues**: https://github.com/your-repo/issues

---

**💡 Dica**: Para desenvolvimento ativo, use setup local. Para testes de integração e staging, use Docker.
