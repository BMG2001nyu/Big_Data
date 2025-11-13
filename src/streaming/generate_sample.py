"""Generate sample streaming aggregates from processed datasets."""
from __future__ import annotations

import argparse
import logging
import pathlib

import pandas as pd


def build_sample_aggregates(processed_path: pathlib.Path, output_path: pathlib.Path) -> None:
    if not processed_path.exists():
        raise FileNotFoundError(f"No processed data at {processed_path}")

    logging.info("Generating streaming aggregates from dataset %s", processed_path)
    df = pd.read_parquet(processed_path, engine="pyarrow")
    if df.empty:
        raise ValueError("Processed dataset is empty; cannot build streaming aggregates")

    df["from_hour"] = pd.to_datetime(df["from_hour"])
    df = df.dropna(subset=["from_hour", "borough", "roadwayname", "vehicle_count"])

    df.set_index("from_hour", inplace=True)
    aggregates = (
        df.groupby(["borough", "roadwayname"])
        .resample("15min")["vehicle_count"].mean()
        .reset_index()
    )
    aggregates.rename(columns={"from_hour": "window_start", "vehicle_count": "avg_vehicle_count"}, inplace=True)
    aggregates["avg_vehicle_count"] = aggregates["avg_vehicle_count"].fillna(0.0).astype(float)
    aggregates["window_end"] = aggregates["window_start"] + pd.Timedelta(minutes=15)
    aggregates["window_start"] = aggregates["window_start"].astype(str)
    aggregates["window_end"] = aggregates["window_end"].astype(str)

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "sample.parquet"
    aggregates.to_parquet(output_file, index=False)
    logging.info("Wrote sample streaming aggregates to %s", output_file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create sample streaming aggregates")
    parser.add_argument("processed_path", type=pathlib.Path)
    parser.add_argument("--output-path", type=pathlib.Path, default=pathlib.Path("data/stream/aggregates"))
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    build_sample_aggregates(args.processed_path, args.output_path)


if __name__ == "__main__":
    main()

