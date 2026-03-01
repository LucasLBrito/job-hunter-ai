@echo off
echo Iniciando servidor Uvicorn em background...
start /B venv\Scripts\python -m uvicorn app.main:app --port 8001 > uvicorn_output.log 2>&1

echo Aguardando 10 segundos para inicializacao...
timeout /t 10 /nobreak > NUL

echo Rodando Seed Script...
set API_URL=http://localhost:8001/api/v1
venv\Scripts\python seed_preferences.py

echo.
echo Check uvicorn_output.log se falhar.
echo Para parar o servidor, execute: taskkill /F /IM python.exe (CUIDADO)
