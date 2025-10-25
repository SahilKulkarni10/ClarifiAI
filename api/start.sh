#!/bin/bash
# Start script for Render deployment

set -e  # Exit on error

echo "🚀 Starting ClariFi AI API via run.py..."
echo "🐍 Python version: $(python --version)"

# Run the Python startup script with proper error handling
exec python run.py
