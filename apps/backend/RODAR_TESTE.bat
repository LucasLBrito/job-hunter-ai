@echo off
echo.
echo ========================================
echo  Job Hunter AI - Teste Ultra Simples
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Verificando Python...
py --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo [2/4] Criando/Ativando ambiente virtual...
if not exist venv (
    py -m venv venv
)
call venv\Scripts\activate.bat

echo.
echo [3/4] Instalando FastAPI e Uvicorn...
py -m pip install --upgrade pip --quiet
py -m pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 --quiet

echo.
echo [4/4] Iniciando servidor...
echo.
echo ========================================
echo  SERVIDOR RODANDO!
echo.
echo  Acesse no navegador:
echo  - http://localhost:8000
echo  - http://localhost:8000/health  
echo  - http://localhost:8000/docs
echo.
echo  Pressione CTRL+C para parar
echo ========================================
echo.

py main_simple.py
