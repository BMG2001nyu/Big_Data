#!/bin/bash
# Quick setup script for MongoDB integration

set -e

echo "🚀 Setting up MongoDB for Traffic Analytics..."

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB doesn't appear to be running."
    echo "   Please start MongoDB first:"
    echo "   macOS: brew services start mongodb-community"
    echo "   Linux: sudo systemctl start mongod"
    exit 1
fi

echo "✅ MongoDB is running"

# Install Python dependencies if needed
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Load CSV data
echo "📥 Loading CSV data into MongoDB..."
python scripts/load_csv_to_mongodb.py --csv data/raw/7ym2-wayt.csv

# Load anomalies if they exist
if [ -f "data/anomalies/anomaly_events.parquet" ]; then
    echo "📥 Loading anomaly data..."
    python scripts/load_anomalies_to_mongodb.py
fi

# Generate stream aggregates
echo "📊 Generating stream aggregates..."
python scripts/generate_stream_aggregates.py --limit 200

echo ""
echo "✅ MongoDB setup complete!"
echo ""
echo "You can now start the API server:"
echo "  uvicorn src.api.app:app --reload"
echo ""
echo "And start the dashboard:"
echo "  cd dashboard && npm run dev"
echo ""

