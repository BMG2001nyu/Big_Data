"""Dask-based ETL pipeline for NYC traffic volume data."""
from __future__ import annotations

import argparse
import logging
import pathlib
from typing import Optional

import dask.dataframe as dd


def read_raw(input_path: str, assume_missing: bool = True) -> dd.DataFrame:
    path = pathlib.Path(input_path)
    if path.is_dir():
        logging.info("Reading parquet directory %s", input_path)
        return dd.read_parquet(input_path, engine="pyarrow")
    if input_path.endswith(".parquet"):
        logging.info("Reading parquet file %s", input_path)
        return dd.read_parquet(input_path, engine="pyarrow")

    logging.info("Reading CSV data %s", input_path)
    return dd.read_csv(
        input_path,
        assume_missing=assume_missing,
        blocksize="64MB",
        parse_dates=["fromhour", "tohour"],
    )


def clean(ddf: dd.DataFrame) -> dd.DataFrame:
    logging.info("Transforming dataset with Dask")
    ddf = ddf.dropna(subset=["fromhour", "tohour", "vehiclecount"])
    ddf = ddf.assign(
        from_hour=ddf["fromhour"],
        to_hour=ddf["tohour"],
        vehicle_count=ddf["vehiclecount"],
    )
    duration_minutes = (ddf["to_hour"] - ddf["from_hour"]) / dd.to_timedelta(1, "m")
    duration_minutes = duration_minutes.replace({0: None})
    ddf = ddf.assign(duration_minutes=duration_minutes)
    ddf = ddf.assign(
        volume_per_minute=ddf["vehicle_count"] / duration_minutes,
        date=ddf["from_hour"].dt.date,
        hour=ddf["from_hour"].dt.hour,
        weekday=ddf["from_hour"].dt.day_name().str[:3],
    )
    ddf = ddf.assign(is_weekend=ddf["weekday"].isin(["Sat", "Sun"]))
    ddf = ddf.assign(borough=ddf["borough"].str.upper())

    # Baselines for congestion indices
    borough_hour_avg = ddf.groupby(["borough", "hour"])["vehicle_count"].transform("mean")
    weekpart_avg = ddf.groupby(["borough", "roadwayname", "is_weekend"])["vehicle_count"].transform("mean")
    ddf = ddf.assign(
        avg_volume_borough_hour=borough_hour_avg,
        avg_volume_weekpart=weekpart_avg,
        congestion_index=ddf["vehicle_count"] / borough_hour_avg.replace({0: None}),
        weekpart_congestion_ratio=ddf["vehicle_count"] / weekpart_avg.replace({0: None}),
    )

    # Peak-hour identification (top 3 per date/borough/roadway)
    hourly_volume = (
        ddf.groupby(["date", "borough", "roadwayname", "hour"])["vehicle_count"]
        .mean()
        .reset_index()
    )
    hourly_volume["volume_rank"] = hourly_volume.groupby(["date", "borough", "roadwayname"])[
        "vehicle_count"
    ].rank(method="dense", ascending=False)
    hourly_volume["is_peak_hour"] = hourly_volume["volume_rank"] <= 3

    ddf = ddf.merge(
        hourly_volume[["date", "borough", "roadwayname", "hour", "is_peak_hour"]],
        on=["date", "borough", "roadwayname", "hour"],
        how="left",
    )

    ddf = ddf.drop(columns=[col for col in ["fromhour", "tohour", "vehiclecount"] if col in ddf.columns])

    return ddf


def write_processed(ddf: dd.DataFrame, output_path: str, partition_on: Optional[list[str]] = None) -> None:
    logging.info("Writing processed dataset to %s", output_path)
    ddf.to_parquet(output_path, engine="pyarrow", write_index=False, partition_on=partition_on)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Dask ETL for NYC traffic data")
    parser.add_argument("input_path", help="Path to raw traffic CSV/parquet data")
    parser.add_argument("output_path", help="Destination parquet directory")
    parser.add_argument("--partition-on", nargs="*", default=["date", "borough"])
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    ddf = read_raw(args.input_path)
    transformed = clean(ddf)
    write_processed(transformed, args.output_path, args.partition_on)


if __name__ == "__main__":
    main()

