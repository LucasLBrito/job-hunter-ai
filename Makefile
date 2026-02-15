# Job Hunter AI - Makefile (Estrutura Organizada)
.PHONY: help dev prod stop clean logs test shell migrate

# Detectar OS
ifeq ($(OS),Windows_NT)
    DOCKER_COMPOSE := docker-compose
    SCRIPT_EXT := .bat
    SCRIPT_DIR := scripts\
else
    DOCKER_COMPOSE := docker compose
    SCRIPT_EXT := .sh
    SCRIPT_DIR := scripts/
endif

# Caminhos atualizados
DOCKER_DIR := docker
APPS_DIR := apps
DOCS_DIR := docs

help: ## Mostrar esta ajuda
	@echo "Job Hunter AI - Comandos Disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# SETUP
setup-docker: ## Setup inicial com Docker
	@echo "🐳 Configurando ambiente Docker..."
ifeq ($(OS),Windows_NT)
	$(SCRIPT_DIR)setup\setup-docker.bat
else
	bash $(SCRIPT_DIR)setup/setup-docker.sh
endif

setup-local: ## Setup inicial sem Docker
	@echo "🏠 Configurando ambiente local..."
ifeq ($(OS),Windows_NT)
	$(SCRIPT_DIR)setup\setup-local.bat
else
	bash $(SCRIPT_DIR)setup/setup-local.sh
endif

# DOCKER COMMANDS
dev: ## Subir ambiente de desenvolvimento (Docker)
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml up -d
	@echo "✅ Ambiente dev rodando!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend: http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"

dev-build: ## Rebuild e subir ambiente de desenvolvimento
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml up -d --build

prod: ## Subir ambiente de produção (Docker)
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.prod.yml up -d
	@echo "✅ Ambiente produção rodando!"

prod-build: ## Rebuild e subir ambiente de produção
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.prod.yml up -d --build

stop: ## Parar todos os containers
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml down
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.prod.yml down

clean: ## Limpar containers, volumes e cache
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml down -v
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.prod.yml down -v
	rm -rf data/ logs/ $(APPS_DIR)/frontend/.next/ $(APPS_DIR)/frontend/node_modules/.cache/

# LOGS
logs: ## Ver logs de todos os serviços (dev)
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml logs -f

logs-backend: ## Ver logs apenas do backend (dev)
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml logs -f backend

logs-frontend: ## Ver logs apenas do frontend (dev)
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml logs -f frontend

ps: ## Ver status dos containers
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml ps

# SHELL ACCESS
shell-backend: ## Acessar shell do backend
	docker exec -it jobhunter-backend-dev bash

shell-frontend: ## Acessar shell do frontend
	docker exec -it jobhunter-frontend-dev sh

# TESTING
test: ## Rodar testes do backend
	docker exec jobhunter-backend-dev pytest -v

test-cov: ## Rodar testes com coverage
	docker exec jobhunter-backend-dev pytest --cov=app --cov-report=html

# DATABASE
migrate: ## Rodar migrations
	docker exec jobhunter-backend-dev alembic upgrade head

migrate-create: ## Criar nova migration
	@read -p "Nome da migration: " name; \
	docker exec jobhunter-backend-dev alembic revision --autogenerate -m "$$name"

# UTILITIES
superuser: ## Criar superuser
	docker exec -it jobhunter-backend-dev python -m app.scripts.create_superuser

health: ## Verificar health dos serviços
	@echo "🔍 Verificando saúde dos serviços..."
	@curl -s http://localhost:8000/health | jq || echo "❌ Backend offline"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend online" || echo "❌ Frontend offline"
	@docker exec jobhunter-redis-dev redis-cli ping > /dev/null && echo "✅ Redis online" || echo "❌ Redis offline"

backup: ## Backup do banco de dados
	@mkdir -p backups
	docker cp jobhunter-backend-dev:/app/data/database.db ./backups/backup-$(shell date +%Y%m%d-%H%M%S).db
	@echo "✅ Backup criado em backups/"

restore: ## Restaurar banco de dados (use: make restore FILE=backup.db)
	@if [ -z "$(FILE)" ]; then echo "❌ Use: make restore FILE=path/to/backup.db"; exit 1; fi
	docker cp $(FILE) jobhunter-backend-dev:/app/data/database.db
	@echo "✅ Banco restaurado!"

# DEPENDENCIES
install-deps-backend: ## Instalar dependências do backend
	docker exec jobhunter-backend-dev pip install -r requirements.txt -r requirements-dev.txt

install-deps-frontend: ## Instalar dependências do frontend
	docker exec jobhunter-frontend-dev npm install

# CODE QUALITY
format: ## Formatar código (black + ruff)
	docker exec jobhunter-backend-dev black app/
	docker exec jobhunter-backend-dev ruff check app/ --fix

lint: ## Lint do código
	docker exec jobhunter-backend-dev ruff check app/
	docker exec jobhunter-backend-dev mypy app/

# LOCAL DEVELOPMENT
local-backend: ## Iniciar backend localmente
ifeq ($(OS),Windows_NT)
	$(SCRIPT_DIR)start\start-backend-local.bat
else
	bash $(SCRIPT_DIR)start/start-backend-local.sh
endif

local-frontend: ## Iniciar frontend localmente
ifeq ($(OS),Windows_NT)
	$(SCRIPT_DIR)start\start-frontend-local.bat
else
	bash $(SCRIPT_DIR)start/start-frontend-local.sh
endif

# RESTART
restart-backend: ## Restart apenas backend
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml restart backend

restart-frontend: ## Restart apenas frontend
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml restart frontend

# MONITORING
stats: ## Ver estatísticas de uso dos containers
	docker stats --no-stream

watch: ## Watch logs em tempo real (dev)
	$(DOCKER_COMPOSE) -f $(DOCKER_DIR)/docker-compose.dev.yml logs -f --tail=100

# DOCUMENTATION
docs: ## Abrir documentação principal
	@echo "📚 Documentação disponível:"
	@echo "   README.md"
	@echo "   $(DOCS_DIR)/DOCKER_SETUP.md"
	@echo "   $(DOCS_DIR)/LOCAL_SETUP.md"
	@echo "   $(DOCS_DIR)/DOCKER_VS_LOCAL.md"
	@echo "   PROJECT_STRUCTURE.md"
