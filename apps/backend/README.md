# 🐍 Job Hunter AI - Backend

API REST desenvolvida com **FastAPI** e **SQLAlchemy Async**.

## 🛠️ Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (Prod) / SQLite (Dev - Async via Aiosqlite)
- **ORM**: SQLAlchemy 2.0 (Async) + Alembic
- **AI**: Gemini 1.5 Pro / Flash, OpenAI GPT-4o
- **Auth**: JWT (OAuth2)

## 🚀 Setup Local

### 1. Ambiente Virtual

```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Dependências

```bash
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente

Copie o `.env.example` para `.env`:

```bash
cp .env.example .env
```

Preencha as chaves de API (Gemini, etc.).

### 4. Banco de Dados

```bash
# Criar migrações (se alterou models)
alembic revision --autogenerate -m "mensagem"

# Aplicar migrações
alembic upgrade head
```

### 5. Rodar Servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Docker Production

O backend possui um `Dockerfile` otimizado para produção.

```bash
docker build -t jobhunter-backend .
docker run -p 8080:8080 jobhunter-backend
```

**Nota:** O script `scripts/start_prod.py` é o entrypoint oficial, garantindo:
1. Verificação de dependências (`asyncpg`, `greenlet`).
2. Execução de migrações (`alembic upgrade head`) com timeout.
3. Inicialização do `uvicorn` na porta correta.

## 🧪 Estrutura

- `app/api/`: Rotas (v1)
- `app/core/`: Configurações (config.py)
- `app/db/`: Conexão e Sessão DB
- `app/models/`: Modelos SQLAlchemy
- `app/schemas/`: Modelos Pydantic
- `app/services/`: Lógica de Negócio (Scrapers, Analyzers)
