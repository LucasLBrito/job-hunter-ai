# 🌟 Job Hunter AI

[![React](https://img.shields.io/badge/Frontend-React.js-blue?style=flat&logo=react)](apps/frontend) 
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](apps/backend)
[![Docker](https://img.shields.io/badge/Deploy-Docker-2496ED?style=flat&logo=docker)](docker)

> O **Job Hunter AI** é um sistema de automação inteligente construído com o propósito de revolucionar a busca por empregos. Ele funciona como um agente autônomo 24/7 que busca, analisa e filtra as melhores vagas para o seu perfil em diversas plataformas trabalhando de forma autônoma.

## ✨ Features Principais

- 🤖 **Agente IA Autônomo** - Busca ativa e análise de compatibilidade de vagas usando IA (Gemini/OpenAI).
- 🕷️ **Multi-Platform Scraper** - Coleta vagas simultaneamente em **LinkedIn, Indeed, Glassdoor e Adzuna**.
- 📄 **Análise de Currículo** - Extração inteligente de habilidades usando **Azure Document Intelligence** e **LLMs**.
- 💬 **Integração WhatsApp** - Alertas instantâneos e interação via chat diretamente pelo seu smartphone.
- 🏢 **Match Inteligente** - Sistema de "Scoring" que dá uma nota (0-100%) para cada vaga baseado no seu currículo.
- 📊 **Dashboard Moderno** - Central de comando Next.js limpa e responsiva para gerenciar todas as suas candidaturas (em construção).

## 🛠️ Tecnologias Utilizadas

Este projeto segue uma arquitetura baseada em **Monorepo**, dividindo claramente o ecossistema:

| Camada | Tecnologias Principais |
|---|---|
| **Frontend** | Next.js 14, React, TailwindCSS, ShadcnUI |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy (Async), Pydantic V2 |
| **Database** | PostgreSQL (Produção), SQLite (Dev/Testes) |
| **Inteligência Artificial** | Google Gemini 1.5 Flash/Pro, OpenAI GPT-4o, Azure AI |
| **Infraestrutura** | Docker, Docker Compose, Railway (Deploy), Render |

---

## 📂 Visão Geral da Estrutura

Para entender em profundidade o que cada pasta faz, consulte os READMEs específicos clicando nos links abaixo:

```text
job-hunter-ai/
├── apps/                    # Aplicações principais do projeto
│   ├── backend/             # 🐍 API em FastAPI (Lógica de IA, Scrapers, Banco de dados)
│   └── frontend/            # ⚛️ Interface visual em Next.js
├── data/                    # Bancos de dados locais (SQLite) 
├── docker/                  # 🐳 Arquivos Docker Compose para Dev e Produção
├── docs/                    # Documentações gerais
│   └── history/             # Logs e históricos de desenvolvimento antigos
└── scripts/                 # ⚙️ Automações para facilitar o uso
    ├── setup/               # Scripts para preparar o ambiente
    ├── start/               # Scripts para rodar os servidores
    ├── verification/        # Scripts de teste e manutenção
    └── windows/             # Scripts legados / utilitários para Windows
```

👉 **Acesso rápido aos guias detalhados:**
- [Como funciona o Backend](apps/backend/README.md)
- [Como funciona o Frontend](apps/frontend/README.md)
- [Como usar os Scripts de automação](scripts/README.md)
- [Como rodar usando Docker](docker/README.md)

---

## 🚀 Como Rodar o Projeto

Você tem duas formas de rodar o repositório localmente. A mais recomendada e fácil é via **Docker**.

### Opção 1: Usando Docker (Recomendado)

> Consulte o guia completo em [**docker/README.md**](docker/README.md).

1. Preencha as chaves de API necessárias (Gemini, Azure, etc.) copiando o arquivo `.env.example` para `.env` tanto no backend quanto no frontend.
2. Na raiz do projeto, execute:
   ```bash
   docker-compose -f docker/docker-compose.dev.yml up -d --build
   ```
3. Acesse:
   - Frontend: `http://localhost:3000`
   - Backend API Docs: `http://localhost:8000/docs`

### Opção 2: Usando Scripts Nativos (Local)

> Ideal para Desenvolvimento Ativo. Consulte o guia [**scripts/README.md**](scripts/README.md).

O projeto conta com scripts prontos na pasta `scripts/start` para facilitar o inicio dos serivdores sem precisar digitar comandos longos toda hora.
Basta executar `scripts/start/start-backend-local.bat` (ou `.sh` no linux/mac).

---

## 🤝 Como Contribuir

Fique à vontade para reportar bugs através das **Issues** ou enviar **Pull Requests**. 
Antes de codar, recomendamos fortemente a leitura do nosso [Guia de Contribuição](CONTRIBUTING.md) para entender nossos padrões de *commits* e *branches*.
