FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para compilação (ex: uvicorn/gunicorn) e scrapers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para cachear as dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código fonte
COPY . .

# Variáveis de ambiente default (podem ser sobrescritas pelo docker-compose)
ENV PYTHONPATH=/app
ENV PORT=8000
ENV HOST=0.0.0.0

# Expor a porta
EXPOSE 8000

# Script de inicialização que roda migrações e sobe o servidor
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --forwarded-allow-ips '*'"]
