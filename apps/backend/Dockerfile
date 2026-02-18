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

# DEBUG: List files to verify script existence
RUN ls -R /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the application
# Run the application using shell to allow variable expansion
CMD ["python", "-u", "scripts/start_prod.py"]
