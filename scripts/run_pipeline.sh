#!/usr/bin/env bash
set -euo pipefail

RAW_DIR="data/raw"
PROCESSED_DIR="data/processed"
ANOMALY_PATH="data/anomalies/anomaly_events.parquet"
DASK_PROCESSED_DIR="data/processed_dask"

python -m src.ingestion.download_data --limit "${DOWNLOAD_LIMIT:-}" || true
python -m src.processing.pyspark_etl "$RAW_DIR" "$PROCESSED_DIR"
if [[ "${USE_DASK_ETL:-}" != "" ]]; then
  python -m src.processing.dask_etl "$RAW_DIR" "$DASK_PROCESSED_DIR"
fi
python -m src.anomaly.detect "$PROCESSED_DIR" --output-path "$ANOMALY_PATH" --summary-path reports/anomaly_summary.json
python -m src.ml.train_predict "$PROCESSED_DIR"
python -m src.ml.evaluate models reports/model_performance.md
python -m src.recommendations.generator "$PROCESSED_DIR" --output reports/recommendations.json
python -m src.streaming.generate_sample "$PROCESSED_DIR" --output-path data/stream/aggregates
