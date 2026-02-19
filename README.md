# 🌟 Job Hunter AI

**Sistema completo de automação de busca, análise e aplicação de vagas de emprego com IA.**

Destrua a barreira da busca de emprego com um agente autônomo que trabalha 24/7 para você.

## ✨ Features Principais

- 🤖 **Agente IA Autônomo** - Busca, analisa e (futuramente) aplica em vagas automaticamente.
- 🕷️ **Multi-Platform Scraper** - Busca vagas em **LinkedIn, Indeed, Glassdoor e Adzuna** simultaneamente (via `python-jobspy`).
- 📄 **Análise de Currículo** - Extração inteligente de skills via **Azure Document Intelligence** e **Gemini 1.5 Pro**.
- 💬 **Integração WhatsApp** - Receba notificações de novas vagas e responda questionários diretamente pelo WhatsApp.
- 🏢 **Match Inteligente** - Scoring de compatibilidade (0-100%) baseado no seu perfil e requisitos da vaga.
- 📊 **Dashboard Moderno** - Interface React/Next.js para gerenciar candidaturas e visualizar insights.
- 🐳 **Docker Native** - Ambiente de desenvolvimento e produção 100% containerizado.

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, React, TailwindCSS, ShadcnUI.
- **Backend**: FastAPI (Python 3.11), SQLAlchemy (Async), Pydantic V2.
- **Database**: PostgreSQL (Production), SQLite (Dev/Fallback).
- **AI/ML**: Google Gemini 1.5 Flash/Pro, OpenAI GPT-4o (Opcional).
- **Infra**: Docker, Docker Compose, Railway (Deploy).

## 🚀 Quick Start (Docker)

### Pré-requisitos
- Docker & Docker Compose
- Python 3.11+ (opcional, para scripts locais)

### 1. Configuração Inicial

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/job-hunter-ai.git
cd job-hunter-ai

# 2. Configurar Variáveis de Ambiente
# Backend
cp apps/backend/.env.example apps/backend/.env
# Frontend
cp apps/frontend/.env.example apps/frontend/.env.local
```

### 2. Edite os arquivos `.env`
Preencha as chaves de API necessárias (Gemini, Azure, etc.) em `apps/backend/.env`.

### 3. Rodar a Aplicação

```bash
# Iniciar tudo (Frontend + Backend + Banco)
docker-compose -f docker/docker-compose.dev.yml up -d --build
```

Acesse:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Logs**: `docker-compose -f docker/docker-compose.dev.yml logs -f`

## 📦 Estrutura do Projeto

```
job-hunter-ai/
├── apps/
│   ├── backend/           # FastAPI Application
│   └── frontend/          # Next.js Application
├── docker/                # Docker Compose files
├── scripts/
│   ├── verification/      # Scripts de teste/verificação
│   └── start/             # Scripts de inicialização
└── README.md              # Este arquivo
```

## 🚢 Deploy (Railway)

O projeto está configurado para deploy contínuo no **Railway**.

1. Crie um projeto no Railway.
2. Conecte seu repositório GitHub.
3. Adicione um serviço **PostgreSQL**.
4. Configure as variáveis de ambiente no Railway (copie do `.env`).
5. O deploy será automático usando o `Dockerfile` na raiz de `apps/backend`.

## 🧪 Testes e Verificação

Scripts úteis para verificar o funcionamento do sistema estão em `scripts/verification/`:

```bash
# Verificar banco de dados
python scripts/verification/check_db.py

# Verificar fluxo de vagas
python scripts/verification/verify_jobs_flow.py
```

## 🤝 Contribuição

Sinta-se livre para abrir Issues e Pull Requests.

## 📝 Licença

MIT
