"""FastAPI service exposing traffic analytics endpoints."""
from __future__ import annotations

import asyncio
import json
import pathlib
from typing import List

import pandas as pd
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from src.recommendations.generator import RecommendationConfig, RecommendationGenerator

PROCESSED_PATH = pathlib.Path("data/processed")
ANOMALY_PATH = pathlib.Path("data/anomalies/anomaly_events.parquet")
STREAM_OUTPUT_PATH = pathlib.Path("data/stream/aggregates")

app = FastAPI(title="NYC Traffic Analytics API")


def load_latest_parquet(path: pathlib.Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist")
    if path.is_file():
        return pd.read_parquet(path)
    parquet_files = list(path.glob("**/*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"No parquet files under {path}")
    latest = max(parquet_files, key=lambda file: file.stat().st_mtime)
    return pd.read_parquet(latest)


@app.get("/traffic/summary")
@app.get("/api/traffic/summary", include_in_schema=False)
def traffic_summary() -> List[dict]:
    try:
        df = load_latest_parquet(PROCESSED_PATH)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if "date" not in df.columns:
        df["date"] = pd.to_datetime(df["from_hour"]).dt.date
    if "borough" not in df.columns:
        df["borough"] = df.get("roadwayname", "UNKNOWN")
    summary = (
        df.groupby(["date", "borough"])["vehicle_count"]
        .sum()
        .reset_index()
        .tail(100)
    )
    return summary.to_dict(orient="records")


@app.get("/traffic/anomalies")
@app.get("/api/traffic/anomalies", include_in_schema=False)
def traffic_anomalies(limit: int = 100) -> List[dict]:
    try:
        df = load_latest_parquet(ANOMALY_PATH)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return df.sort_values("from_hour", ascending=False).head(limit).to_dict(orient="records")


@app.get("/traffic/recommendations")
@app.get("/api/traffic/recommendations", include_in_schema=False)
def traffic_recommendations(top_k: int = 10) -> List[dict]:
    if not PROCESSED_PATH.exists():
        raise HTTPException(status_code=404, detail=f"Processed path {PROCESSED_PATH} not found")
    config = RecommendationConfig(processed_path=PROCESSED_PATH, top_k=top_k)
    generator = RecommendationGenerator(config)
    try:
        df = generator.load_data()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    recommendations = generator.generate(df)
    return recommendations[:top_k]


@app.get("/traffic/stream/aggregates")
@app.get("/api/traffic/stream/aggregates", include_in_schema=False)
def traffic_stream_aggregates(limit: int = 50) -> List[dict]:
    if not STREAM_OUTPUT_PATH.exists():
        return []
    parquet_files = list(STREAM_OUTPUT_PATH.glob("**/*.parquet"))
    if not parquet_files:
        return []
    df = (
        pd.concat((pd.read_parquet(file) for file in parquet_files), ignore_index=True)
        .dropna(subset=["window_start", "borough"])
        .sort_values("window_end")
    )
    for numeric_column in ("avg_vehicle_count", "weekend_ratio", "avg_congestion"):
        if numeric_column in df.columns:
            df[numeric_column] = pd.to_numeric(df[numeric_column], errors="coerce").fillna(0.0)
    if "window_start" in df.columns:
        df["window_start"] = pd.to_datetime(df["window_start"]).astype(str)
    if "window_end" in df.columns:
        df["window_end"] = pd.to_datetime(df["window_end"]).astype(str)
    records = df.tail(limit).to_dict(orient="records")
    sanitized = json.loads(json.dumps(records, default=str, allow_nan=False))
    return sanitized


@app.websocket("/ws/traffic")
async def traffic_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            try:
                payload = traffic_stream_aggregates(limit=20)
            except HTTPException:
                payload = []
            await websocket.send_text(json.dumps({"type": "stream_update", "data": payload}))
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        return


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
