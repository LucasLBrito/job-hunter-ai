# Job Hunter AI - Docker Setup

## 🚀 Quick Start

### Desenvolvimento

```bash
# Subir todos os serviços em modo desenvolvimento
docker-compose -f docker-compose.dev.yml up -d

# Ver logs
docker-compose -f docker-compose.dev.yml logs -f

# Parar serviços
docker-compose -f docker-compose.dev.yml down
```

**URLs de acesso:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redis: localhost:6379

### Produção

```bash
# Build e subir em modo produção
docker-compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Parar serviços
docker-compose -f docker-compose.prod.yml down
```

## 📋 Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo
- 10GB espaço em disco

## 🔧 Configuração

### 1. Variáveis de Ambiente

#### Backend - Desenvolvimento (`backend/.env.dev`)
```bash
# LLM Configuration
OPENAI_API_KEY=sk-your-key-here
# OU
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key-here

# WhatsApp Business API
WHATSAPP_API_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id

# Database
DATABASE_URL=sqlite:///./data/database.db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Frontend - Desenvolvimento (`frontend/.env.dev`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Backend - Produção (`backend/.env.prod`)
```bash
# Mesmo que .env.dev mas com valores de produção
# IMPORTANTE: Trocar SECRET_KEY!
SECRET_KEY=production-secret-key-256-bits-long
ALLOWED_ORIGINS=https://yourdomain.com
```

#### Frontend - Produção (`frontend/.env.prod`)
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### 2. Estrutura de Diretórios

```
job-hunter-ai/
├── backend/
│   ├── Dockerfile          # Produção
│   ├── Dockerfile.dev      # Desenvolvimento
│   ├── .env.dev
│   ├── .env.prod
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile          # Produção
│   ├── Dockerfile.dev      # Desenvolvimento
│   ├── .env.dev
│   └── .env.prod
├── data/                   # SQLite database (persiste)
├── logs/                   # Application logs
├── docker-compose.dev.yml
└── docker-compose.prod.yml
```

## 🐳 Serviços Docker

### Desenvolvimento

| Serviço | Container | Porta | Descrição |
|---------|-----------|-------|-----------|
| backend | jobhunter-backend-dev | 8000 | FastAPI com hot reload |
| frontend | jobhunter-frontend-dev | 3000 | Next.js com hot reload |
| redis | jobhunter-redis-dev | 6379 | Cache e queue |
| agent-scheduler | jobhunter-scheduler-dev | - | Background jobs |

### Produção

| Serviço | Container | Porta | Descrição |
|---------|-----------|-------|-----------|
| backend | jobhunter-backend-prod | 8000 | FastAPI otimizado (4 workers) |
| frontend | jobhunter-frontend-prod | 3000 | Next.js standalone build |
| redis | jobhunter-redis-prod | - | Cache e queue |
| agent-scheduler | jobhunter-scheduler-prod | - | Background jobs |
| nginx | jobhunter-nginx-prod | 80/443 | Reverse proxy (opcional) |

## 🛠️ Comandos Úteis

### Desenvolvimento

```bash
# Rebuild apenas um serviço
docker-compose -f docker-compose.dev.yml up -d --build backend

# Acessar shell do container
docker exec -it jobhunter-backend-dev bash

# Ver logs de um serviço específico
docker-compose -f docker-compose.dev.yml logs -f backend

# Rodar migrations
docker exec jobhunter-backend-dev python -m alembic upgrade head

# Criar superuser
docker exec -it jobhunter-backend-dev python -m app.scripts.create_superuser

# Rodar testes
docker exec jobhunter-backend-dev pytest
```

### Produção

```bash
# Restart de um serviço
docker-compose -f docker-compose.prod.yml restart backend

# Ver status dos containers
docker-compose -f docker-compose.prod.yml ps

# Ver uso de recursos
docker stats

# Backup do banco de dados
docker cp jobhunter-backend-prod:/app/data/database.db ./backup-$(date +%Y%m%d).db

# Ver logs de erros
docker-compose -f docker-compose.prod.yml logs --tail=100 backend | grep ERROR
```

## 🔍 Troubleshooting

### Container não sobe

```bash
# Ver logs detalhados
docker-compose -f docker-compose.dev.yml logs backend

# Verificar variáveis de ambiente
docker exec jobhunter-backend-dev env | grep API_KEY
```

### Hot reload não funciona (Windows)

```bash
# Usar polling ao invés de file watching
# Adicionar ao docker-compose.dev.yml no serviço frontend:
environment:
  - CHOKIDAR_USEPOLLING=true
```

### Problemas de permissão (Linux)

```bash
# Ajustar permissões dos volumes
sudo chown -R $USER:$USER ./data ./logs
```

### Reset completo

```bash
# CUIDADO: Remove TODOS os dados!
docker-compose -f docker-compose.dev.yml down -v
rm -rf data/ logs/
docker-compose -f docker-compose.dev.yml up -d --build
```

## 📊 Monitoramento

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Redis
docker exec jobhunter-redis-dev redis-cli ping
```

### Metrics (Produção)

```bash
# Ver uso de CPU/RAM
docker stats --no-stream

# Logs estruturados
docker-compose -f docker-compose.prod.yml logs --since=1h backend | jq
```

## 🚢 Deploy para Produção

### Railway / Fly.io

1. **Build e push da imagem:**
```bash
docker build -t jobhunter-backend -f backend/Dockerfile backend/
docker tag jobhunter-backend registry.railway.app/jobhunter-backend
docker push registry.railway.app/jobhunter-backend
```

2. **Configurar variáveis de ambiente** no painel da plataforma

3. **Deploy:**
```bash
railway up
# ou
flyctl deploy
```

### VPS/Servidor Próprio

```bash
# No servidor
git clone <repo>
cd job-hunter-ai
cp backend/.env.example backend/.env.prod
cp frontend/.env.example frontend/.env.prod

# Editar .env.prod com valores reais
nano backend/.env.prod
nano frontend/.env.prod

# Subir em produção
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🔐 Segurança

### Checklist de Produção

- [ ] Trocar `SECRET_KEY` por valor aleatório de 256 bits
- [ ] Configurar HTTPS/SSL (via Nginx ou Cloudflare)
- [ ] Limitar `ALLOWED_ORIGINS` apenas para domínios confiáveis
- [ ] Usar API keys específicas de produção
- [ ] Configurar firewall (permitir apenas portas 80/443)
- [ ] Habilitar rate limiting no Nginx
- [ ] Configurar backup automático do banco
- [ ] Monitorar logs de segurança

## 📚 Próximos Passos

1. ✅ Configurar variáveis de ambiente
2. ✅ Testar em desenvolvimento
3. [ ] Implementar backend (Fase 2-8)
4. [ ] Implementar frontend (Fase 9)
5. [ ] Testes end-to-end
6. [ ] Deploy em staging
7. [ ] Deploy em produção
