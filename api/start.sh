#!/bin/bash
# Render startup script with better error handling

set -e  # Exit on error

echo "🚀 Starting ClariFi AI Backend..."
echo "Python version: $(python --version)"
echo "PORT: $PORT"
echo "ENVIRONMENT: $ENVIRONMENT"

# Check if PORT is set
if [ -z "$PORT" ]; then
    echo "❌ ERROR: PORT environment variable is not set"
    exit 1
fi

echo "✅ PORT is set to: $PORT"

# Check critical environment variables
if [ -z "$MONGODB_URI" ] && [ -z "$MONGODB_URL" ]; then
    echo "⚠️  WARNING: MongoDB URI not set - app will run without database"
fi

# Test that we can import the app
echo "🔍 Testing app import..."
python -c "from main import app; print('✅ App imported successfully')" || {
    echo "❌ Failed to import app"
    exit 1
}

# Start uvicorn
echo "🌐 Starting uvicorn server on 0.0.0.0:$PORT"
exec uvicorn main:app --host 0.0.0.0 --port $PORT --log-level info --timeout-keep-alive 10
