#!/bin/bash
# Start the FastAPI server with MongoDB connection

cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🚀 Starting FastAPI server..."
echo "📊 MongoDB connection: Checking..."
echo "🌐 API will be available at: http://localhost:8008"
echo "📖 API docs at: http://localhost:8008/docs"
echo ""

# Start uvicorn on port 8008 (dashboard expects this port)
uvicorn src.api.app:app --host 0.0.0.0 --port 8008 --reload

