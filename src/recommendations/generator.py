"""Generate congestion mitigation recommendations from analytics datasets."""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class RecommendationConfig:
    processed_path: pathlib.Path
    top_k: int = 10
    congestion_threshold: float = 1.4
    weekend_ratio_threshold: float = 1.3


class RecommendationGenerator:
    def __init__(self, config: RecommendationConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_data(self) -> pd.DataFrame:
        if not self.config.processed_path.exists():
            raise FileNotFoundError(f"Processed path {self.config.processed_path} not found")
        self.logger.info("Loading processed dataset for recommendations from %s", self.config.processed_path)
        df = pd.read_parquet(self.config.processed_path, engine="pyarrow")
        df = df.dropna(subset=["vehicle_count", "congestion_index", "weekpart_congestion_ratio"])
        return df

    def generate(self, df: pd.DataFrame) -> List[dict]:
        aggregations = (
            df.groupby(["borough", "roadwayname", "is_peak_hour"])
            .agg(
                avg_congestion=("congestion_index", "mean"),
                peak_hours=("hour", lambda hours: sorted(set(hours))),
                weekend_ratio=("weekpart_congestion_ratio", "mean"),
                avg_volume=("vehicle_count", "mean"),
            )
            .reset_index()
        )

        top_segments = (
            aggregations[aggregations["is_peak_hour"]]
            .sort_values("avg_congestion", ascending=False)
            .head(self.config.top_k)
        )

        recommendations: List[dict] = []
        for _, row in top_segments.iterrows():
            actions = []
            if row["avg_congestion"] >= self.config.congestion_threshold:
                actions.append("Adjust signal timing to prioritize throughput during peak window")
            if row["weekend_ratio"] >= self.config.weekend_ratio_threshold:
                actions.append("Deploy targeted weekend traffic advisories and dynamic signage")
            if row["avg_volume"] >= 1500:
                actions.append("Evaluate reversible lanes or ramp metering during identified hours")
            if not actions:
                actions.append("Monitor conditions and update congestion models with fresh data")

            recommendations.append(
                {
                    "borough": row["borough"],
                    "roadway": row["roadwayname"],
                    "peak_hours": row["peak_hours"],
                    "avg_congestion": round(row["avg_congestion"], 3),
                    "weekend_ratio": round(row["weekend_ratio"], 3),
                    "actions": actions,
                }
            )
        return recommendations

    def save(self, recommendations: List[dict], output_path: pathlib.Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(recommendations, indent=2), encoding="utf-8")
        self.logger.info("Saved %d recommendations to %s", len(recommendations), output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate congestion mitigation recommendations")
    parser.add_argument("processed_path", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("reports/recommendations.json"))
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--congestion-threshold", type=float, default=1.4)
    parser.add_argument("--weekend-threshold", type=float, default=1.3)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    config = RecommendationConfig(
        processed_path=args.processed_path,
        top_k=args.top_k,
        congestion_threshold=args.congestion_threshold,
        weekend_ratio_threshold=args.weekend_threshold,
    )
    generator = RecommendationGenerator(config)
    df = generator.load_data()
    recommendations = generator.generate(df)
    generator.save(recommendations, args.output)


if __name__ == "__main__":
    main()

