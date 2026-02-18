FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY railway_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r railway_requirements.txt

# Copy application code
COPY . .

# Create directory for uploaded files and data
RUN mkdir -p /app/uploads /app/data

# Expose port - Railway injects PORT env var (usually 8080)
ENV PORT=8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the application
# Run the application using shell to allow variable expansion
CMD ["python", "-u", "scripts/start_prod.py"]
