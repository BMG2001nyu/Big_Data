"""Spark Structured Streaming consumer for traffic data."""
from __future__ import annotations

import argparse
import logging

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def build_spark(app_name: str = "nyc-traffic-stream") -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def run_stream(kafka_bootstrap: str, topic: str, checkpoint_dir: str, output_path: str) -> None:
    spark = build_spark()
    try:
        df = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", kafka_bootstrap)
            .option("subscribe", topic)
            .load()
        )

        parsed = (
            df.selectExpr("CAST(value AS STRING) as json")
            .select(F.from_json("json", "records ARRAY<STRUCT<from_hour: STRING, borough: STRING, roadwayname: STRING, direction: STRING, vehicle_count: DOUBLE, volume_per_minute: DOUBLE>>").alias("payload"))
            .select(F.explode("payload.records").alias("record"))
            .select("record.*")
            .withColumn("from_hour", F.to_timestamp("from_hour"))
        )

        aggregates = (
            parsed.withWatermark("from_hour", "15 minutes")
            .groupBy(
                F.window("from_hour", "15 minutes").alias("window"),
                "borough",
                "roadwayname",
            )
            .agg(F.avg("vehicle_count").alias("avg_vehicle_count"))
            .select(
                F.col("window.start").alias("window_start"),
                F.col("window.end").alias("window_end"),
                "borough",
                "roadwayname",
                "avg_vehicle_count",
            )
        )

        query = (
            aggregates.writeStream.outputMode("append")
            .format("parquet")
            .option("path", output_path)
            .option("checkpointLocation", checkpoint_dir)
            .trigger(processingTime="30 seconds")
            .start()
        )
        query.awaitTermination()
    finally:
        spark.stop()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Consume traffic data stream and aggregate metrics")
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="nyc_traffic")
    parser.add_argument("--checkpoint-dir", default="data/checkpoints/stream")
    parser.add_argument("--output-path", default="data/stream/aggregates")
    args = parser.parse_args()
    run_stream(args.bootstrap_servers, args.topic, args.checkpoint_dir, args.output_path)


if __name__ == "__main__":
    main()
