# NYC Traffic Volume Analytics Platform

End-to-end big data solution analyzing New York City automated traffic volume counts. The project covers ingestion, scalable processing, machine learning, anomaly detection, streaming, and interactive dashboards.

## Project Layout

```
├── config/                # Storage configuration
├── data/                  # Raw, processed, intermediate data
├── docs/                  # Architecture and dashboard documentation
├── models/                # Trained ML artifacts and metrics
├── notebooks/             # Exploration and feature analysis workbooks
├── reports/               # Generated reports
├── scripts/               # Pipeline orchestration scripts
├── src/
│   ├── ingestion/         # Data download and staging
│   ├── processing/        # PySpark ETL pipelines
│   │   └── dask_etl.py     # Dask fallback ETL for constrained environments
│   ├── utils/             # Feature engineering utilities
│   ├── ml/                # Model training and evaluation
│   ├── anomaly/           # Isolation Forest anomaly detection
│   ├── streaming/         # Kafka producer and Spark streaming consumer
│   └── api/               # FastAPI service for dashboards
├── dashboard/             # React dashboard (Vite + React Query)
├── tests/                 # Unit tests
└── scripts/run_pipeline.sh
```

## Getting Started

1. **Install dependencies**
   - Python ≥ 3.10, PySpark, pandas, scikit-learn, xgboost, requests, FastAPI, uvicorn, kafka-python
   - Node ≥ 18 for the dashboard (`cd dashboard && npm install`)

2. **Configure storage**
   - Update `config/storage.yaml` with the appropriate HDFS, local, or cloud paths.

3. **Run the batch pipeline**
   ```bash
   chmod +x scripts/run_pipeline.sh
   DOWNLOAD_LIMIT=10000 ./scripts/run_pipeline.sh
   ```

   - Set `USE_DASK_ETL=1` to run the Dask pipeline alongside PySpark.

4. **Serve the API**
   ```bash
   uvicorn src.api.app:app --reload
   ```

5. **Start the dashboard**
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

6. **Streaming prototype (optional)**
   - Start Kafka locally or use cloud managed Kafka
   ```bash
   python src/streaming/producer.py data/processed/sample.parquet --topic nyc_traffic
   python -m pyspark src/streaming/consumer.py --topic nyc_traffic
   ```
   - The batch pipeline also generates sample aggregates (`src/streaming/generate_sample.py`) so dashboards have baseline data even without Kafka.
   - Live aggregates are available via `/api/traffic/stream/aggregates` and WebSocket `/ws/traffic`.

7. **Generate recommendations manually**
   ```bash
   python src/recommendations/generator.py data/processed --output reports/recommendations.json
   ```

## Testing

Run unit tests with pytest:
```bash
pytest
```

## Documentation

- Architecture overview: `docs/architecture.md`
- Dashboard setup: `docs/dashboard_setup.md` (to be filled with deployment details)
- Tableau and advanced visuals: `docs/visualization_resources.md`
- Model performance reports: `reports/model_performance.md`
- Recommendation outputs: `reports/recommendations.json`
- Anomaly summaries: `reports/anomaly_summary.json`

## Roadmap

- Integrate weather/event data
- Enhance anomaly detection with advanced models
- Productionize streaming pipeline with robust monitoring
- Expand dashboard with congestion forecasts and recommendation widgets
