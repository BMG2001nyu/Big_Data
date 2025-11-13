"""PySpark ETL pipeline for NYC traffic volume data."""
from __future__ import annotations

import argparse
import logging
import pathlib
from typing import Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.utils.feature_builders import (
    add_congestion_indices,
    add_peak_hour_flags,
    add_temporal_features,
)


def build_spark(app_name: str = "nyc-traffic-etl") -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def read_raw_traffic(spark: SparkSession, input_path: str, limit: Optional[int] = None) -> DataFrame:
    logging.info("Reading raw data from %s", input_path)
    df = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .csv(input_path)
    )
    if limit:
        df = df.limit(limit)
    return df


def clean_traffic(df: DataFrame) -> DataFrame:
    logging.info("Cleaning dataset and standardizing columns")
    timestamp = F.to_timestamp(
        F.format_string(
            "%s-%02d-%02d %02d:%02d:00",
            F.col("yr"),
            F.col("m"),
            F.col("d"),
            F.col("hh"),
            F.col("mm"),
        ),
        "yyyy-M-d HH:mm:ss",
    )

    cleaned = (
        df.dropna(subset=["vol", "street", "boro", "segmentid"])
        .withColumn("from_hour", timestamp)
        .withColumn("vehicle_count", F.col("vol").cast("double"))
        .withColumn("duration_minutes", F.lit(15.0))
        .withColumn("borough", F.upper(F.col("boro")))
        .withColumn("roadwayname", F.col("street"))
        .withColumn("direction", F.upper(F.col("direction")))
        .withColumn("segment_id", F.col("segmentid"))
        .withColumn("from_street", F.col("fromst"))
        .withColumn("to_street", F.col("tost"))
        .drop("vol", "boro", "street", "segmentid", "fromst", "tost", "yr", "m", "d", "hh", "mm")
    )

    cleaned = cleaned.withColumn(
        "volume_per_minute",
        F.when(F.col("duration_minutes") > 0, F.col("vehicle_count") / F.col("duration_minutes")),
    )

    enhanced = add_temporal_features(
        cleaned.withColumn("date", F.to_date("from_hour"))
    ).withColumnRenamed("day_of_week", "weekday")
    enhanced = add_peak_hour_flags(enhanced)
    enhanced = add_congestion_indices(enhanced)
    return enhanced


def write_processed(df: DataFrame, output_path: str, partition_cols: Optional[list[str]] = None) -> None:
    logging.info("Writing processed data to %s", output_path)
    writer = df.write.mode("overwrite").format("parquet")
    if partition_cols:
        writer = writer.partitionBy(*partition_cols)
    writer.save(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PySpark ETL for NYC traffic data")
    parser.add_argument("input_path", help="Path to raw traffic CSV files")
    parser.add_argument("output_path", help="Destination for processed parquet files")
    parser.add_argument("--limit", type=int, default=None, help="Optional record limit for testing")
    parser.add_argument(
        "--partition-cols",
        nargs="*",
        default=None,
        help="Columns to partition the output parquet by",
    )
    return parser.parse_args()


def run_etl(input_path: str, output_path: str, limit: Optional[int] = None, partition_cols: Optional[list[str]] = None) -> None:
    spark = build_spark()
    try:
        raw_df = read_raw_traffic(spark, input_path, limit)
        cleaned_df = clean_traffic(raw_df)
        write_processed(cleaned_df, output_path, partition_cols)
    finally:
        spark.stop()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    run_etl(args.input_path, args.output_path, args.limit, args.partition_cols)


if __name__ == "__main__":
    main()
