"""Isolation Forest based anomaly detection for traffic volume."""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
from dataclasses import dataclass
from typing import Dict, Optional

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


@dataclass
class AnomalyConfig:
    processed_path: pathlib.Path
    output_path: pathlib.Path = pathlib.Path("data/anomalies/anomaly_events.parquet")
    contamination: float = 0.01
    random_state: int = 42
    min_vehicle_count: Optional[int] = None
    summary_path: pathlib.Path = pathlib.Path("reports/anomaly_summary.json")


class AnomalyDetector:
    def __init__(self, config: AnomalyConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> pd.DataFrame:
        if not self.config.processed_path.exists():
            raise FileNotFoundError("Processed path not found")
        self.logger.info("Loading processed parquet dataset from %s", self.config.processed_path)
        df = pd.read_parquet(self.config.processed_path, engine="pyarrow")
        return df

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        feature_cols = [
            "vehicle_count",
            "volume_per_minute",
            "duration_minutes",
        ]
        self.logger.info("Running Isolation Forest on %d rows", len(df))
        model = IsolationForest(
            contamination=self.config.contamination,
            random_state=self.config.random_state,
            n_estimators=300,
        )
        features = df[feature_cols].fillna(0)
        scores = model.fit_predict(features)
        severity = model.decision_function(features)
        df["anomaly_score"] = scores
        df["anomaly_severity"] = -severity  # higher severity = larger positive value
        anomalies = df[df["anomaly_score"] == -1]
        if self.config.min_vehicle_count is not None:
            anomalies = anomalies[anomalies["vehicle_count"] >= self.config.min_vehicle_count]
        self.logger.info("Detected %d anomalies", len(anomalies))
        return anomalies

    def save(self, anomalies: pd.DataFrame) -> None:
        anomalies.to_parquet(self.config.output_path, index=False)
        metadata = {
            "record_count": int(len(anomalies)),
            "output": str(self.config.output_path),
            "borough_breakdown": anomalies.groupby("borough").size().to_dict() if not anomalies.empty else {},
            "top_severity": (
                anomalies.nlargest(5, "anomaly_severity")[
                    ["from_hour", "borough", "roadwayname", "anomaly_severity"]
                ]
                .assign(from_hour=lambda frame: frame["from_hour"].astype(str))
                .to_dict(orient="records")
                if not anomalies.empty
                else []
            ),
        }
        json_path = self.config.output_path.with_suffix(".json")
        json_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        self.logger.info("Saved anomalies to %s", self.config.output_path)
        self._write_summary(anomalies)

    def _write_summary(self, anomalies: pd.DataFrame) -> None:
        summary = {
            "record_count": int(len(anomalies)),
            "average_severity": float(anomalies["anomaly_severity"].mean()) if not anomalies.empty else 0.0,
            "peak_hours": anomalies.groupby("hour").size().nlargest(5).to_dict() if not anomalies.empty else {},
        }
        self.config.summary_path.parent.mkdir(parents=True, exist_ok=True)
        self.config.summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        self.logger.info("Wrote anomaly summary to %s", self.config.summary_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect anomalies in traffic volume data")
    parser.add_argument("processed_path", type=pathlib.Path)
    parser.add_argument("--output-path", type=pathlib.Path, default=pathlib.Path("data/anomalies/anomaly_events.parquet"))
    parser.add_argument("--contamination", type=float, default=0.01)
    parser.add_argument("--min-vehicle-count", type=int, default=None)
    parser.add_argument("--summary-path", type=pathlib.Path, default=pathlib.Path("reports/anomaly_summary.json"))
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    config = AnomalyConfig(
        processed_path=args.processed_path,
        output_path=args.output_path,
        contamination=args.contamination,
        min_vehicle_count=args.min_vehicle_count,
        summary_path=args.summary_path,
    )
    detector = AnomalyDetector(config)
    df = detector.load_data()
    anomalies = detector.detect(df)
    detector.save(anomalies)


if __name__ == "__main__":
    main()
