@echo off
REM Job Hunter AI - Setup Script for Windows

echo ======================================
echo Job Hunter AI - Setup Script (Windows)
echo ======================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker nao esta rodando ou nao esta instalado.
    echo Por favor, instale Docker Desktop: https://docs.docker.com/desktop/windows/install/
    pause
    exit /b 1
)

echo [OK] Docker encontrado
echo.

REM Create directories
echo [INFO] Criando diretorios...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist backups mkdir backups
echo [OK] Diretorios criados
echo.

REM Copy environment files
echo [INFO] Configurando arquivos de ambiente...

if not exist backend\.env.dev (
    copy backend\.env.example backend\.env.dev >nul
    echo [OK] Criado backend\.env.dev
) else (
    echo [INFO] backend\.env.dev ja existe (mantendo)
)

if not exist frontend\.env.dev (
    copy frontend\.env.example frontend\.env.dev >nul
    echo [OK] Criado frontend\.env.dev
) else (
    echo [INFO] frontend\.env.dev ja existe (mantendo)
)

echo.
echo ===============================================
echo [IMPORTANTE] Configure suas API keys!
echo ===============================================
echo.
echo Edite os seguintes arquivos:
echo   - backend\.env.dev  (OpenAI/Anthropic, Azure, WhatsApp)
echo   - frontend\.env.dev (URL da API)
echo.

REM Ask if user wants to start services
set /p START="Deseja iniciar os servicos agora? (s/n): "

if /i "%START%"=="s" (
    echo.
    echo [INFO] Iniciando servicos Docker...
    docker-compose -f docker-compose.dev.yml up -d --build
    
    echo.
    echo [OK] Servicos iniciados!
    echo.
    echo Acesse:
    echo   Frontend: http://localhost:3000
    echo   Backend:  http://localhost:8000
    echo   API Docs: http://localhost:8000/docs
    echo.
    echo Ver logs:
    echo   docker-compose -f docker-compose.dev.yml logs -f
    echo.
    echo Parar servicos:
    echo   docker-compose -f docker-compose.dev.yml down
) else (
    echo.
    echo Para iniciar os servicos manualmente, execute:
    echo   docker-compose -f docker-compose.dev.yml up -d
)

echo.
echo [OK] Setup completo!
echo.
echo Comandos uteis:
echo   docker-compose -f docker-compose.dev.yml up -d     - Iniciar servicos
echo   docker-compose -f docker-compose.dev.yml logs -f   - Ver logs
echo   docker-compose -f docker-compose.dev.yml down      - Parar servicos
echo   docker-compose -f docker-compose.dev.yml ps        - Ver status
echo.

pause
