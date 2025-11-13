from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pandas as pd

from src.recommendations.generator import RecommendationConfig, RecommendationGenerator


def test_recommendation_generator_creates_actions(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "borough": ["MANHATTAN"] * 4,
            "roadwayname": ["FDR Drive"] * 4,
            "hour": [8, 9, 10, 11],
            "is_peak_hour": [True, True, False, False],
            "vehicle_count": [2500, 2400, 1200, 900],
            "congestion_index": [1.6, 1.5, 0.9, 0.7],
            "weekpart_congestion_ratio": [1.4, 1.35, 0.95, 0.85],
        }
    )
    parquet_dir = tmp_path / "processed"
    parquet_dir.mkdir()
    df.to_parquet(parquet_dir / "part.parquet")

    config = RecommendationConfig(processed_path=parquet_dir, top_k=3)
    generator = RecommendationGenerator(config)
    recommendations = generator.generate(generator.load_data())

    assert recommendations
    first = recommendations[0]
    assert "actions" in first and first["actions"]

    output_path = tmp_path / "recommendations.json"
    generator.save(recommendations, output_path)
    saved = json.loads(output_path.read_text())
    assert saved

