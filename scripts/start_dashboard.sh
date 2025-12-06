#!/bin/bash
# Start the React dashboard

cd "$(dirname "$0")/../dashboard"

echo "🚀 Starting Dashboard..."
echo "📊 Make sure the API is running on http://localhost:8008"
echo "🌐 Dashboard will be available at: http://localhost:8009"
echo ""

npm run dev

