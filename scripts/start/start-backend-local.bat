@echo off
REM Start Backend Server Locally (Windows)

cd backend

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment nao encontrado
    echo Execute setup-local.bat primeiro
    pause
    exit /b 1
)

REM Check if .env.local exists
if not exist .env.local (
    echo [WARNING] .env.local nao encontrado, usando valores padrao
)

echo ========================================
echo Iniciando Backend FastAPI...
echo ========================================
echo.
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo Para parar: Ctrl+C
echo.

REM Start with reload for development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --env-file .env.local
