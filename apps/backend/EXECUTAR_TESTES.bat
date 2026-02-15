@echo off
echo.
echo ========================================
echo  Job Hunter AI - Teste Funcional Completo
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando se servidor esta rodando...
curl -s http://localhost:8000/health > nul
if errorlevel 1 (
    echo.
    echo ⚠️  SERVIDOR NAO DETECTADO!
    echo    Iniciando servidor em nova janela...
    start "Job Hunter Server" cmd /k "venv\Scripts\activate & py main_simple.py"
    
    echo    Aguardando inicializacao (5s)...
    timeout /t 5 > nul
) else (
    echo ✅ Servidor ja esta rodando!
)

echo.
echo [2/3] Executando testes funcionais...
echo.
python TESTE_FUNCIONAL.py

echo.
echo ========================================
echo  Teste concluido!
echo ========================================
if errorlevel 1 (
   echo ❌ ALGUNS TESTES FALHARAM
)
pause
