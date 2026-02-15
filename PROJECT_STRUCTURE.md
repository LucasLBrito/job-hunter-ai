# 📁 Job Hunter AI - Estrutura Organizada

```
job-hunter-ai/
├── 📄 README.md                    # Documentação principal
│
├── 📂 apps/                        # Aplicações
│   ├── backend/                    # FastAPI backend
│   │   ├── app/                    # Código da aplicação
│   │   ├── tests/                  # Testes
│   │   ├── alembic/                # Database migrations
│   │   ├── Dockerfile              # Prod
│   │   ├── Dockerfile.dev          # Dev
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   └── frontend/                   # Next.js frontend
│       ├── app/                    # Next.js 14 App Router
│       ├── components/             # React components
│       ├── lib/                    # Utilities
│       ├── public/                 # Static assets
│       ├── Dockerfile              # Prod
│       ├── Dockerfile.dev          # Dev
│       ├── package.json
│       └── .env.example
│
├── 📂 scripts/                     # Scripts de setup e automação
│   ├── setup/                      # Scripts de instalação
│   │   ├── setup-docker.sh
│   │   ├── setup-docker.bat
│   │   ├── setup-local.sh
│   │   └── setup-local.bat
│   │
│   ├── start/                      # Scripts de inicialização
│   │   ├── start-backend.sh
│   │   ├── start-backend.bat
│   │   ├── start-frontend.sh
│   │   └── start-frontend.bat
│   │
│   └── utils/                      # Utilitários
│       ├── backup-db.sh
│       ├── restore-db.sh
│       └── generate-secret.py
│
├── 📂 docker/                      # Configurações Docker
│   ├── docker-compose.dev.yml
│   ├── docker-compose.prod.yml
│   ├── nginx/                      # Nginx config para prod
│   │   └── nginx.conf
│   └── .dockerignore
│
├── 📂 docs/                        # Documentação
│   ├── DOCKER_SETUP.md
│   ├── LOCAL_SETUP.md
│   ├── DOCKER_VS_LOCAL.md
│   ├── API_REFERENCE.md           # (futuro)
│   └── CONTRIBUTING.md            # (futuro)
│
├── 📂 shared/                      # Código compartilhado
│   ├── types/                      # TypeScript types
│   └── schemas/                    # Pydantic schemas
│
├── 📂 data/                        # Dados persistentes
│   └── .gitkeep
│
├── 📂 logs/                        # Application logs
│   └── .gitkeep
│
├── 📂 backups/                     # Database backups
│   └── .gitkeep
│
├── 📄 Makefile                     # Comandos automatizados
├── 📄 .gitignore
└── 📄 LICENSE

```

## 🎯 Benefícios da Nova Estrutura

### 1. **Separação Clara**
- `apps/` - Código das aplicações
- `scripts/` - Todos os scripts em um só lugar
- `docker/` - Configurações Docker isoladas
- `docs/` - Documentação organizada

### 2. **Raiz Limpa**
- Apenas README.md, Makefile e .gitignore na raiz
- Fácil navegação
- Profissional

### 3. **Escalabilidade**
- Fácil adicionar novos apps
- Scripts organizados por função
- Docs expandíveis

### 4. **Padrão Monorepo**
- Segue convenções de Nx/Turborepo
- Facilita migração futura para ferramentas de monorepo

## 🔄 Migração

Todos os arquivos foram reorganizados para a nova estrutura. Para usar:

1. **Docker**:
   ```bash
   docker-compose -f docker/docker-compose.dev.yml up -d
   ```
   
   Ou use o Makefile (atualizado automaticamente):
   ```bash
   make dev
   ```

2. **Local**:
   ```bash
   # Windows
   scripts\setup\setup-local.bat
   scripts\start\start-backend.bat
   scripts\start\start-frontend.bat
   
   # Linux/Mac
   scripts/setup/setup-local.sh
   scripts/start/start-backend.sh
   scripts/start/start-frontend.sh
   ```

## 📝 Makefile Atualizado

O Makefile foi atualizado para usar os novos caminhos automaticamente. Todos os comandos continuam funcionando:

```bash
make setup    # Usa scripts/setup/
make dev      # Usa docker/docker-compose.dev.yml  
make logs     # Funciona igual
make test     # Funciona igual
```

---

**✅ Estrutura mais profissional, organizada e escalável!**
