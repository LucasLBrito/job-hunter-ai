#!/bin/bash
set -e

echo "-----------------------------------"
echo "Job Hunter AI - Production Startup"
echo "-----------------------------------"

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo "ERROR: alembic not found in PATH"
    exit 1
fi

echo "Running Database Migrations..."
# Try running migrations
if alembic upgrade head; then
    echo "Migrations SUCCESS"
else
    echo "Migrations FAILED"
    # Don't exit, try to start app anyway to see logs? 
    # Or exit to prevent broken app? 
    # Better exit to fail deployment if DB is wrong.
    exit 1
fi

echo "Starting Uvicorn Server on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
