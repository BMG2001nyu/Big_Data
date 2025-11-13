from __future__ import annotations

from datetime import datetime

from pyspark.sql import SparkSession

from src.utils.feature_builders import add_temporal_features


def test_add_temporal_features() -> None:
    spark = SparkSession.builder.master("local[1]").appName("unit-test").getOrCreate()
    try:
        df = spark.createDataFrame(
            [(datetime(2024, 1, 1, 8, 30),)],
            ["from_hour"],
        )
        transformed = add_temporal_features(df)
        row = transformed.collect()[0]
        assert row.hour == 8
        assert row.day_of_week == "Mon"
        assert row.is_weekend is False
    finally:
        spark.stop()
