# 🚀 Starting the Application

## Quick Start

### Terminal 1: Start API Server (MongoDB Backend)
```bash
cd /Users/ashah6/Desktop/Big_Data
source venv/bin/activate
uvicorn src.api.app:app --host 0.0.0.0 --port 8008 --reload
```

Or use the script:
```bash
./scripts/start_api.sh
```

**API will be available at:**
- API: http://localhost:8008
- Docs: http://localhost:8008/docs
- Health: http://localhost:8008/health

### Terminal 2: Start Dashboard (Frontend)
```bash
cd /Users/ashah6/Desktop/Big_Data/dashboard
npm run dev
```

Or use the script:
```bash
./scripts/start_dashboard.sh
```

**Dashboard will be available at:**
- http://localhost:8009

---

## Verify Everything is Working

### 1. Check MongoDB Connection
```bash
curl http://localhost:8008/health
```

Should return:
```json
{
  "status": "ok",
  "mongodb": "connected",
  "collections": ["traffic_summary", "traffic_raw"]
}
```

### 2. Check API Endpoints
```bash
# Traffic summary
curl http://localhost:8008/api/traffic/summary

# Anomalies
curl http://localhost:8008/api/traffic/anomalies
```

### 3. Open Dashboard
Open your browser to: **http://localhost:8009**

The dashboard will automatically connect to the API and display data from MongoDB!

---

## Data Flow

```
MongoDB (traffic_analytics)
    ↓
FastAPI (localhost:8008)
    ↓
React Dashboard (localhost:8009)
```

---

## Troubleshooting

### API not starting?
- Make sure MongoDB is running: `mongosh traffic_analytics --eval "db.traffic_summary.countDocuments()"`
- Check if port 8008 is available: `lsof -i :8008`

### Dashboard not connecting?
- Make sure API is running on port 8008
- Check browser console for errors
- Verify API is accessible: `curl http://localhost:8008/health`

### No data showing?
- Check MongoDB has data: `mongosh traffic_analytics --eval "db.traffic_summary.countDocuments()"`
- Verify API returns data: `curl http://localhost:8008/api/traffic/summary`

