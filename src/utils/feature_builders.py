"""Utilities for feature engineering on NYC traffic datasets."""
from __future__ import annotations

from typing import Iterable

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def add_temporal_features(df: DataFrame) -> DataFrame:
    """Add temporal context features to the dataset."""
    return (
        df.withColumn("hour", F.hour("from_hour"))
        .withColumn("day_of_week", F.date_format("from_hour", "E"))
        .withColumn("is_weekend", F.col("day_of_week").isin("Sat", "Sun"))
        .withColumn("week_of_year", F.weekofyear("from_hour"))
    )


def add_lag_features(df: DataFrame, partition_cols: Iterable[str], order_col: str, lags: Iterable[int]) -> DataFrame:
    """Add lagged vehicle count features using window functions."""
    window_spec = Window.partitionBy(*partition_cols).orderBy(order_col)
    result = df
    for lag in lags:
        result = result.withColumn(f"vehicle_count_lag_{lag}", F.lag("vehicle_count", lag).over(window_spec))
    return result


def add_rolling_features(df: DataFrame, partition_cols: Iterable[str], order_col: str, windows: Iterable[int]) -> DataFrame:
    """Add rolling average features for vehicle volume."""
    result = df
    for window in windows:
        result = result.withColumn(
            f"vehicle_count_roll_{window}",
            F.avg("vehicle_count").over(
                Window.partitionBy(*partition_cols)
                .orderBy(order_col)
                .rowsBetween(-window, 0)
            ),
        )
    return result


def add_spatial_features(df: DataFrame) -> DataFrame:
    """Derive spatial features such as sensor density proxies."""
    return df.withColumn("location_key", F.concat_ws("_", F.col("borough"), F.col("roadwayname")))


def add_peak_hour_flags(df: DataFrame) -> DataFrame:
    """Mark peak congestion hours per date/borough/roadway combination."""
    grouping_cols = ["date", "borough", "roadwayname"]
    rank_window = Window.partitionBy(*grouping_cols).orderBy(F.col("vehicle_count").desc())
    ranked = df.withColumn("volume_rank", F.dense_rank().over(rank_window))
    return ranked.withColumn("is_peak_hour", F.col("volume_rank") <= F.lit(3)).drop("volume_rank")


def add_congestion_indices(df: DataFrame) -> DataFrame:
    """Compute congestion indices comparing against borough/hour and weekday/weekend baselines."""
    borough_hour_window = Window.partitionBy("borough", "hour")
    weekend_window = Window.partitionBy("borough", "roadwayname", "is_weekend")

    with_averages = (
        df.withColumn("avg_volume_borough_hour", F.avg("vehicle_count").over(borough_hour_window))
        .withColumn("avg_volume_weekpart", F.avg("vehicle_count").over(weekend_window))
    )

    congestion = with_averages.withColumn(
        "congestion_index",
        F.when(F.col("avg_volume_borough_hour") == 0, F.lit(0.0)).otherwise(
            (F.col("vehicle_count") / F.col("avg_volume_borough_hour")).cast("double")
        ),
    ).withColumn(
        "weekpart_congestion_ratio",
        F.when(F.col("avg_volume_weekpart") == 0, F.lit(0.0)).otherwise(
            (F.col("vehicle_count") / F.col("avg_volume_weekpart")).cast("double")
        ),
    )

    return congestion
