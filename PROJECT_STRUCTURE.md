# 📂 Job Hunter AI - Estrutura do Projeto

Estrutura organizada seguindo o padrão Monorepo.

```
job-hunter-ai/
├── 📄 README.md                    # Documentação principal
├── 📄 Makefile                     # Comandos úteis (make dev, make prod)
│
├── 📂 apps/                        # Aplicações
│   ├── backend/                    # FastAPI
│   │   ├── app/                    # Código Fonte
│   │   ├── alembic/                # Migrações DB
│   │   ├── scripts/                # Scripts backend (start_prod.py)
│   │   ├── Dockerfile              # Prod Docker image
│   │   └── README.md
│   │
│   └── frontend/                   # Next.js
│       ├── app/                    # App Router source
│       ├── components/             # React Components
│       ├── Dockerfile              # Prod Docker image
│       └── README.md
│
├── 📂 scripts/                     # Scripts de automação e utilitários
│   ├── verification/               # Scripts de teste/verificação (check_db.py, etc)
│   ├── setup/                      # Scripts de ambiente
│   └── start/                      # Helpers de inicialização
│
├── 📂 docker/                      # Configurações Docker Compose
│   ├── docker-compose.dev.yml
│   └── docker-compose.prod.yml
│
└── 📂 docs/                        # Documentação detalhada
    ├── LOCAL_SETUP.md
    └── DOCKER_SETUP.md
```

## 💡 Organização

- **apps/**: Contém o código fonte isolado de cada serviço.
- **scripts/verification/**: Contém scripts Python para validar banco de dados, fluxos de API e integridade do sistema.
- **docker/**: Arquivos de orquestração de containers.
