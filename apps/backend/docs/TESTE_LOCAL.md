# 🧪 Guia de Teste Rápido - Backend FastAPI

## 🚀 Setup Rápido (5 minutos)

### 1. Instalar Dependências

```bash
# Navegar para o backend
cd apps/backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Verificar Configuração

O arquivo `.env.local` já está configurado com valores padrão para teste.

**⚠️ IMPORTANTE**: Para funcionalidades completas, você precisará:
- OpenAI API Key OU Anthropic API Key (para análise IA)
- Azure Document Intelligence (para análise de currículo)
- WhatsApp Business API (para notificações)

**Para teste básico** (sem API keys):
- O backend vai iniciar normalmente
- Endpoints `/` e `/health` funcionarão
- Database será criado automaticamente
- Funcionalidades de IA estarão desabilitadas

### 3. Iniciar Backend

```bash
# Opção 1: Via uvicorn direto
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opção 2: Via Python
python -m uvicorn app.main:app --reload

# Opção 3: Via script (se preferir)
python app/main.py
```

Aguarde a mensagem:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting up Job Hunter AI...
INFO:     Environment: development
INFO:     Database initialized
INFO:     Application startup complete.
```

## 🧪 Testando os Endpoints

### 1. Endpoint Root

```bash
# Browser
http://localhost:8000

# cURL
curl http://localhost:8000
```

**Resposta esperada:**
```json
{
  "message": "Job Hunter AI API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

### 2. Health Check

```bash
# Browser
http://localhost:8000/health

# cURL
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

### 3. Swagger UI (Documentação Interativa)

```bash
# Browser
http://localhost:8000/docs
```

Você verá a interface Swagger com todos os endpoints disponíveis!

### 4. ReDoc (Documentação Alternativa)

```bash
# Browser
http://localhost:8000/redoc
```

## 📊 Verificações

### Verificar Database Criado

```bash
# No diretório raiz do projeto
dir data\database.db

# Ou conectar com SQLite
sqlite3 data/database.db
.tables
.quit
```

Você deve ver as tabelas: `users`, `jobs`, `resumes`, `applications`

### Ver Logs

Os logs aparecerão no terminal onde você executou `uvicorn`:

```
2026-02-15 12:40:00 - app.main - INFO - Starting up Job Hunter AI...
2026-02-15 12:40:00 - app.main - INFO - Environment: development
2026-02-15 12:40:00 - app.main - INFO - Database initialized
```

## 🎯 Próximos Testes (Após Implementar Endpoints)

Quando os endpoints de autenticação estiverem prontos:

### 1. Criar Usuário

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "username": "testuser"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "securepassword123"
  }'
```

### 3. Listar Jobs

```bash
curl http://localhost:8000/api/v1/jobs \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'app'"

**Solução**: Certifique-se de estar no diretório `apps/backend` e que o venv está ativado.

```bash
cd apps/backend
venv\Scripts\activate
```

### Erro: "sqlite3.OperationalError: unable to open database file"

**Solução**: O diretório `data/` não existe. Crie manualmente:

```bash
# No diretório raiz do projeto
mkdir data
```

### Porta 8000 já em uso

**Solução**: Use outra porta:

```bash
uvicorn app.main:app --reload --port 8001
```

### Secret Key Warning

**Solução**: Isso é normal em desenvolvimento. Para produção, gere uma chave segura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

E atualize no `.env.local`

## ✅ Checklist de Validação

- [ ] Backend iniciou sem erros
- [ ] Endpoint `/` respondeu com JSON
- [ ] Endpoint `/health` retornou "healthy"
- [ ] Swagger UI (`/docs`) acessível
- [ ] Database `data/database.db` foi criado
- [ ] Logs aparecem no terminal
- [ ] Hot reload funciona (mude algo em `main.py` e salve)

## 🎉 Próximos Passos

1. ✅ Backend rodando localmente
2. ⏳ Implementar endpoints de autenticação (signup, login)
3. ⏳ Implementar CRUD de jobs
4. ⏳ Implementar upload de currículo
5. ⏳ Integrar LLMs para análise
6. ⏳ Desenvolver frontend Next.js

---

**🎯 Objetivo deste teste**: Validar que a estrutura base do FastAPI está funcionando corretamente antes de adicionar funcionalidades complexas.
