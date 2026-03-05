@echo off
echo ==============================================================
echo Iniciando Sessao de 2 Horas do Job Hunter AI (Visibilidade)
echo ==============================================================
echo.
echo Abrindo os seguintes servicos em novas janelas:
echo 1. FastAPI Backend (porta 8000)
echo 2. ETL Worker (Processamento Raw - Postgres)
echo 3. Monitor de Banco de Dados (Estatísticas a cada 10 mins)
echo 4. Scrapy Vagas.com (Coletor Secundário)
echo 5. Scrapy Catho (Coletor Secundário)
echo.

cd apps\backend

REM 1. Start Backend
start "🚀 Job Hunter API" cmd /k "venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM 2. Start Monitor (2 Hours loop)
start "📊 DB Monitor (2 Horas)" cmd /k "venv\Scripts\activate.bat && python scripts\monitor_stats.py"

REM 3. Start ETL Worker
start "⚙️ ETL Worker" cmd /k "venv\Scripts\activate.bat && python etl\worker.py"

REM 4. Start Scrapy Vagas
start "🕷️ Scrapy Vagas" cmd /k "venv\Scripts\activate.bat && cd crawler && scrapy crawl vagas"

REM 5. Start Scrapy Catho
start "🕷️ Scrapy Catho" cmd /k "venv\Scripts\activate.bat && cd crawler && scrapy crawl catho"

echo.
echo Terminais iniciados. Voce pode minimizar esta janela.
echo Pressione qualquer tecla para sair deste lançador.
pause > nul
