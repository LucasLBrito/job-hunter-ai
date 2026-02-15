@echo off
REM Start Frontend Server Locally (Windows)

cd frontend

REM Check if node_modules exists
if not exist node_modules (
    echo [ERROR] node_modules nao encontrado
    echo Execute setup-local.bat primeiro
    pause
    exit /b 1
)

REM Check if .env.local exists
if not exist .env.local (
    echo [WARNING] .env.local nao encontrado, usando valores padrao
)

echo ========================================
echo Iniciando Frontend Next.js...
echo ========================================
echo.
echo URL: http://localhost:3000
echo Para parar: Ctrl+C
echo.

REM Start development server
npm run dev
