.PHONY: setup install dashboard-install ingest etl train anomalies stream test lint api dashboard

setup: install dashboard-install

install:
	pip install -r requirements.txt

requirements.txt:
	@echo "Generate requirements.txt with pinned dependencies." > requirements.txt

dashboard-install:
	cd dashboard && npm install

ingest:
	python src/ingestion/download_data.py

etl:
	python -m pyspark src/processing/pyspark_etl.py data/raw data/processed

dask-etl:
	python src/processing/dask_etl.py data/raw data/processed_dask

train:
	python src/ml/train_predict.py data/processed

anomalies:
	python src/anomaly/detect.py data/processed --summary-path reports/anomaly_summary.json

recommendations:
	python src/recommendations/generator.py data/processed --output reports/recommendations.json

stream:
	python src/streaming/consumer.py

stream-producer:
	python src/streaming/producer.py data/processed/sample.parquet

api:
	uvicorn src.api.app:app --reload

dashboard:
	cd dashboard && npm run dev

test:
	pytest
