#!/bin/bash
# Start script for Render deployment

set -e  # Exit on error

echo "🚀 Starting ClariFi AI API..."
echo "📦 Port: ${PORT:-8000}"
echo "🌍 Environment: ${ENVIRONMENT:-production}"
echo "🐍 Python version: $(python --version)"

# Check if port is set
if [ -z "$PORT" ]; then
    echo "⚠️  PORT environment variable not set, using default 8000"
    export PORT=8000
fi

echo "🔌 Will bind to 0.0.0.0:$PORT"

# Start the application with uvicorn
echo "🎬 Starting uvicorn..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info \
    --timeout-keep-alive 30
