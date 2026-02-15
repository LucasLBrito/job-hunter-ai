@echo off
REM Job Hunter AI - Local Development Setup (No Docker)
REM For Windows

echo ==========================================
echo Job Hunter AI - Setup Local (Sem Docker)
echo ==========================================
echo.

REM Check Python
echo [INFO] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nao encontrado. Instale Python 3.11+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION%

REM Check Node.js
echo [INFO] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js nao encontrado. Instale Node.js 20+
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION%

REM Check Redis (optional)
echo [INFO] Verificando Redis...
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Redis nao encontrado (opcional)
    echo Download: https://github.com/microsoftarchive/redis/releases
) else (
    echo [OK] Redis instalado
)

echo.
echo [INFO] Criando estrutura de diretorios...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist backups mkdir backups

REM Backend setup
echo.
echo [INFO] Configurando Backend Python...
cd backend

REM Create virtual environment
if not exist venv (
    echo    Criando virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Upgrade pip
echo    Atualizando pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies
echo    Instalando dependencias...
if exist requirements.txt (
    pip install -r requirements.txt >nul 2>&1
    echo    [OK] Dependencias backend instaladas
) else (
    echo    [WARNING] requirements.txt nao encontrado
)

REM Copy .env if not exists
if not exist .env.local (
    if exist .env.example (
        copy .env.example .env.local >nul
        echo    [OK] Criado .env.local
    )
)

cd ..

REM Frontend setup
echo.
echo [INFO] Configurando Frontend Node.js...
cd frontend

REM Install dependencies
if exist package.json (
    echo    Instalando dependencias npm...
    call npm install >nul 2>&1
    echo    [OK] Dependencias frontend instaladas
) else (
    echo    [WARNING] package.json nao encontrado
)

REM Copy .env if not exists
if not exist .env.local (
    if exist .env.example (
        copy .env.example .env.local >nul
        echo    [OK] Criado .env.local
    )
)

cd ..

echo.
echo [OK] Setup local completo!
echo.
echo ====================================
echo Proximos passos:
echo ====================================
echo.
echo 1. Configure suas API keys:
echo    - backend\.env.local
echo    - frontend\.env.local
echo.
echo 2. Inicie os servicos:
echo    Terminal 1: local-start-backend.bat
echo    Terminal 2: local-start-frontend.bat
echo.
echo 3. (Opcional) Inicie Redis:
echo    Terminal 3: redis-server
echo.
echo 4. Acesse:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.

pause
