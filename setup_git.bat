@echo off
echo ========================================
echo  Configurando Repositorio Git
echo ========================================

cd /d "%~dp0"

if exist .git (
    echo Ja existe um repositorio Git aqui.
    exit /b 0
)

echo [1/3] Inicializando Git...
git init

echo [2/3] Adicionando arquivos...
git add .

echo [3/3] Criando commit inicial...
git commit -m "feat: Initial project setup (backend + docs + scripts)"

echo.
echo ========================================
echo  Repositorio Configurado com Sucesso!
echo ========================================
