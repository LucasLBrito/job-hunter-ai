# 🌟 Job Hunter AI

Sistema completo de automação de busca e aplicação de vagas de emprego com IA.

## ✨ Features

- 🤖 **Agente IA Autônomo** - Busca, analisa e aplica em vagas automaticamente
- 📄 **Análise de Currículo** - Extração de skills via Azure Document Intelligence
- 💬 **Integração WhatsApp** - Notificações e questionários bidirecionais
- 🏢 **Pesquisa de Empresas** - Análise de cultura e ambiente de trabalho
- 🎯 **Scoring Inteligente** - Match multicritérios com vagas (0-100)
- 📊 **Dashboard React** - Interface completa para gerenciamento
- 🔄 **Aplicação Automática** - LinkedIn Easy Apply e formulários
- ⏰ **Agendamento** - Buscas diárias automáticas

## 🚀 Quick Start

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo

### Instalação

#### Com Docker (Recomendado)

##### Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

##### Windows:
```bash
setup.bat
```

##### Manual:
```bash
# 1. Copiar arquivos de ambiente
cp backend/.env.example backend/.env.dev
cp frontend/.env.example frontend/.env.dev

# 2. Editar com suas API keys
nano backend/.env.dev

# 3. Iniciar serviços
docker-compose -f docker-compose.dev.yml up -d
```

#### Sem Docker (Desenvolvimento Local)

**Pré-requisitos**: Python 3.11+, Node.js 20+, Redis (opcional)

##### Windows:
```bash
setup-local.bat
# Editar backend/.env.local e frontend/.env.local
local-start-backend.bat  # Terminal 1
local-start-frontend.bat # Terminal 2
```

##### Linux/Mac:
```bash
chmod +x setup-local.sh local-start-*.sh
./setup-local.sh
# Editar backend/.env.local e frontend/.env.local
./local-start-backend.sh  # Terminal 1
./local-start-frontend.sh # Terminal 2
```

📖 **Guia completo**: Ver [LOCAL_SETUP.md](LOCAL_SETUP.md)

### Acesso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentação**: http://localhost:8000/docs

## 📁 Estrutura do Projeto

```
job-hunter-ai/
├── apps/                  # Aplicações
│   ├── backend/           # FastAPI + Python
│   └── frontend/          # Next.js 14 + React
├── scripts/               # Scripts de automação
│   ├── setup/             # Setup Docker e Local
│   ├── start/             # Inicialização de serviços
│   └── utils/             # Utilitários
├── docker/                # Configurações Docker
│   ├── docker-compose.dev.yml
│   └── docker-compose.prod.yml
├── docs/                  # Documentação
│   ├── DOCKER_SETUP.md
│   ├── LOCAL_SETUP.md
│   └── DOCKER_VS_LOCAL.md
├── shared/                # Código compartilhado
├── data/                  # SQLite database
├── logs/                  # Application logs
├── backups/               # Database backups
├── Makefile               # Comandos automatizados
└── PROJECT_STRUCTURE.md   # Estrutura detalhada
```

📖 Ver [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) para estrutura completa.

## 🛠️ Comandos Úteis

```bash
# Desenvolvimento
make dev          # Iniciar ambiente dev
make logs         # Ver logs
make test         # Rodar testes
make shell-backend # Acessar shell do backend

# Produção
make prod         # Iniciar ambiente produção
make backup       # Backup do banco
make health       # Verificar saúde dos serviços

# Utilitários
make help         # Ver todos os comandos
make clean        # Limpar tudo
make migrate      # Rodar migrations
```

## 🔧 Configuração

### APIs Necessárias

1. **LLM (escolha um)**:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

2. **Azure Document Intelligence**:
   - https://portal.azure.com/

3. **WhatsApp Business API**:
   - https://business.facebook.com/wa/manage/home/

### Arquivo .env.dev

```bash
# LLM
OPENAI_API_KEY=sk-your-key

# Azure
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://...
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key

# WhatsApp
WHATSAPP_API_TOKEN=your-token
WHATSAPP_PHONE_NUMBER_ID=your-id
```

## 📊 Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend    │────▶│  Agents     │
│  (Next.js)  │     │  (FastAPI)   │     │ (LangGraph) │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Database   │
                    │  (SQLite)    │
                    └──────────────┘
```

## 🧪 Testes

```bash
# Rodar todos os testes
make test

# Com coverage
make test-cov

# Testes específicos
docker exec jobhunter-backend-dev pytest tests/test_agents.py -v
```

## 🚢 Deploy para Produção

### Railway / Fly.io

1. Configure variáveis de ambiente
2. Faça push do código
3. Plataforma faz build automático

### VPS Próprio

```bash
# No servidor
git clone <repo>
cd job-hunter-ai
cp backend/.env.example backend/.env.prod
# Editar .env.prod com valores reais
docker-compose -f docker-compose.prod.yml up -d --build
```

## 📚 Documentação

- [Docker Setup](DOCKER_README.md) - Guia completo Docker
- [Plano de Implementação](../brain/.../implementation_plan.md)
- [Action Items](../brain/.../action_items_detalhados.md)
- [Tasks](../brain/.../task.md)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes

## 🆘 Suporte

- **Issues**: https://github.com/your-repo/issues
- **Docs**: [DOCKER_README.md](DOCKER_README.md)

## 🎯 Roadmap

- [x] Infraestrutura Docker
- [ ] Backend API básica
- [ ] Análise de currículo
- [ ] Integração WhatsApp
- [ ] Scrapers de vagas
- [ ] Frontend Dashboard
- [ ] Aplicação automática
- [ ] Deploy em produção

---

**Desenvolvido com ❤️ usando Next.js, FastAPI e LangGraph**
