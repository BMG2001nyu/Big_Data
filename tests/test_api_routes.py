from __future__ import annotations

import json
from datetime import datetime

import pandas as pd
from fastapi.testclient import TestClient

import src.api.app as api_module


def test_health_endpoint() -> None:
    client = TestClient(api_module.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_stream_aggregates_endpoint(tmp_path, monkeypatch) -> None:
    output_dir = tmp_path / "aggregates"
    output_dir.mkdir()
    sample = pd.DataFrame(
        {
            "window_start": [datetime(2024, 1, 1, 8, 0)],
            "window_end": [datetime(2024, 1, 1, 8, 15)],
            "borough": ["MANHATTAN"],
            "roadwayname": ["FDR Drive"],
            "avg_vehicle_count": [2200.0],
        }
    )
    sample.to_parquet(output_dir / "sample.parquet", index=False)

    monkeypatch.setattr(api_module, "STREAM_OUTPUT_PATH", output_dir)

    client = TestClient(api_module.app)
    response = client.get("/traffic/stream/aggregates")
    assert response.status_code == 200
    payload = response.json()
    assert payload and payload[0]["borough"] == "MANHATTAN"


def test_websocket_stream_updates(tmp_path, monkeypatch) -> None:
    output_dir = tmp_path / "aggregates"
    output_dir.mkdir()
    sample = pd.DataFrame(
        {
            "window_start": [datetime(2024, 1, 1, 8, 0)],
            "window_end": [datetime(2024, 1, 1, 8, 15)],
            "borough": ["MANHATTAN"],
            "roadwayname": ["FDR Drive"],
            "avg_vehicle_count": [2200.0],
        }
    )
    sample.to_parquet(output_dir / "sample.parquet", index=False)
    monkeypatch.setattr(api_module, "STREAM_OUTPUT_PATH", output_dir)

    async def fast_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(api_module.asyncio, "sleep", fast_sleep)

    client = TestClient(api_module.app)
    with client.websocket_connect("/ws/traffic") as websocket:
        message = websocket.receive_text()
        payload = json.loads(message)
        assert payload["type"] == "stream_update"
        assert payload["data"]

