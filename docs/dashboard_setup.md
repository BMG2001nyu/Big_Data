# Dashboard Setup Guide

## Prerequisites
- Node.js >= 18.0
- API service running locally at `http://localhost:8000`

## Installation
```bash
cd dashboard
npm install
```

## Development
```bash
npm run dev
```
Access the dashboard at `http://localhost:5173`.

## Build for Production
```bash
npm run build
npm run preview
```

## Environment Variables (optional)
Create `.env` in the dashboard directory to configure the API URL:
```
VITE_API_URL=http://localhost:8000
VITE_API_WS_URL=ws://localhost:8000
```
Update the Axios calls in `src/App.tsx` to leverage the environment variable if using non-default endpoints.

## Deployment Recommendations
- Host static assets on Netlify, Vercel, or S3 + CloudFront.
- Secure API endpoints with authentication when exposing publicly.
- Configure CI to build the dashboard on every push and publish artifacts.
- Ensure reverse proxies (NGINX, CloudFront) forward WebSocket traffic to `/ws/traffic` for live monitoring.
