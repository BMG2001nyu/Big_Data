"""Kafka producer for streaming NYC traffic data."""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import time
from typing import Iterator

import pandas as pd
from kafka import KafkaProducer


def chunk_records(df: pd.DataFrame, chunk_size: int) -> Iterator[pd.DataFrame]:
    for start in range(0, len(df), chunk_size):
        yield df.iloc[start : start + chunk_size]


def produce_stream(
    bootstrap_servers: str,
    topic: str,
    data_path: pathlib.Path,
    batch_size: int = 100,
    sleep_seconds: float = 1.0,
) -> None:
    logging.info("Loading data from %s", data_path)
    df = pd.read_parquet(data_path)
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )
    logging.info("Streaming %d records to topic %s", len(df), topic)
    for batch in chunk_records(df, batch_size):
        payload = batch.to_dict(orient="records")
        producer.send(topic, value={"records": payload})
        producer.flush()
        logging.debug("Sent batch of %d records", len(batch))
        time.sleep(sleep_seconds)
    logging.info("Streaming completed")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Simulate streaming traffic data to Kafka")
    parser.add_argument("data_path", type=pathlib.Path, help="Parquet file with processed traffic data")
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="nyc_traffic")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()
    produce_stream(args.bootstrap_servers, args.topic, args.data_path, args.batch_size, args.sleep)


if __name__ == "__main__":
    main()
