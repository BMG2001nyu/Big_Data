# NYC Traffic Analytics Architecture

## Data Sources
- NYC Automated Traffic Volume Counts (historic batch downloads)
- Optional real-time feeds (API or simulated Kafka stream)
- Auxiliary datasets: weather, holidays, events (future integration)

## Storage Layers
1. **Raw zone**: Original CSV/JSON files stored in HDFS (`/data/nyc_traffic/raw`) or local `data/raw/` during development.
2. **Processed zone**: Cleaned and standardized parquet datasets in HDFS (`/data/nyc_traffic/processed`) or local `data/processed/`.
3. **Analytics zone**: Feature engineered tables and model-ready datasets in parquet under `data/intermediate/`.
4. **Dask processed zone**: Optional Dask-generated parquet outputs (`data/processed_dask/`) for environments without Spark clusters.

## Processing Engines
- **PySpark** for distributed ETL, aggregation, window analytics, peak-hour detection, and congestion indexing.
- **Dask** for out-of-core ingestion and ETL, including chunked downloads and feature generation when Spark is unavailable.
- **Pandas** for lightweight local transformations and validation.

## Machine Learning
- Supervised models (Random Forest, XGBoost) for congestion forecasting and congestion classification.
- Isolation Forest for unsupervised anomaly detection with severity scoring and summaries.
- Recommendation engine translating analytics into mitigation actions stored under `reports/recommendations.json`.
- Model artifacts versioned in `models/` with metadata stored alongside evaluation reports and feature importance plots in `reports/plots/`.

## Streaming
- Kafka (or compatible message broker) to ingest near-real-time traffic updates.
- Spark Structured Streaming consumer updates live congestion metrics and anomalies.
- FastAPI provides REST and WebSocket endpoints (`/traffic/stream/aggregates`, `/ws/traffic`) for dashboards to consume.

## Visualization
- React dashboard backed by RESTful APIs in `src/api/`.
- Supplemental analytical dashboards built with Plotly or Tableau.

## Orchestration & Automation
- Batch pipelines executed via `scripts/run_pipeline.sh` or task schedulers (Airflow, cron).
- Continuous integration workflow runs tests, linting, and packaging.

## Security & Governance (Future Work)
- Access control policies for sensitive data.
- Data quality monitoring and alerting.

## Deployment Targets
- Development: local environment using Docker-compose.
- Production: cloud-based Spark cluster (AWS EMR, Databricks) with managed Kafka.
