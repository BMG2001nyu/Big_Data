"""Data ingestion utilities for NYC Automated Traffic Volume Counts dataset."""
from __future__ import annotations

import logging
import os
import pathlib
import sys
from dataclasses import dataclass
from typing import Optional

import requests

DEFAULT_DATASET_ID = "7ym2-wayt"
BASE_URL = "https://data.cityofnewyork.us/resource/{dataset}.csv"
CHUNK_SIZE = 1024 * 1024  # 1MB


@dataclass
class DownloadConfig:
    """Configuration for dataset downloads."""

    dataset_id: str = DEFAULT_DATASET_ID
    output_dir: pathlib.Path = pathlib.Path("data/raw")
    app_token: Optional[str] = None
    limit: Optional[int] = None  # Use for sampling during development
    engine: str = "requests"  # or "dask"
    blocksize: str = "32MB"


class DatasetDownloader:
    """Download NYC traffic datasets from the Socrata API."""

    def __init__(self, config: DownloadConfig) -> None:
        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _build_url(self) -> str:
        params = [
            ("$limit", str(self.config.limit)) if self.config.limit else None,
        ]
        # Filter out None values and join as query string
        query_params = "&".join(
            f"{key}={value}" for key, value in params if value is not None
        )
        url = BASE_URL.format(dataset=self.config.dataset_id)
        return f"{url}?{query_params}" if query_params else url

    def download(self, filename: Optional[str] = None) -> pathlib.Path:
        """Download dataset to the configured output directory."""
        url = self._build_url()
        headers = {}
        if self.config.app_token:
            headers["X-App-Token"] = self.config.app_token

        output_filename = filename or f"{self.config.dataset_id}.csv"
        output_path = self.config.output_dir / output_filename
        self.logger.info("Downloading dataset from %s", url)

        if self.config.engine == "requests":
            with requests.get(url, headers=headers, stream=True, timeout=60) as response:
                response.raise_for_status()
                with output_path.open("wb") as file_obj:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            file_obj.write(chunk)
            self.logger.info("Downloaded dataset to %s", output_path)
            return output_path

        if self.config.engine == "dask":
            try:
                import dask.dataframe as dd
            except ImportError as exc:  # pragma: no cover - handled during runtime
                raise RuntimeError(
                    "Dask is required for engine='dask'. Install dask[complete]."
                ) from exc

            self.logger.info("Loading dataset via Dask from %s", url)
            storage_options = {"headers": headers} if headers else None
            ddf = dd.read_csv(
                url,
                blocksize=self.config.blocksize,
                storage_options=storage_options,
                assume_missing=True,
            )
            parquet_dir = self.config.output_dir / f"{self.config.dataset_id}_dask"
            parquet_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Writing Dask dataframe to parquet at %s", parquet_dir)
            ddf.to_parquet(parquet_dir, engine="pyarrow", write_index=False)
            return parquet_dir

        raise ValueError(f"Unsupported engine {self.config.engine}")


def main(argv: list[str]) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    limit: Optional[int] = None
    app_token = os.getenv("NYC_OPENDATA_APP_TOKEN")
    engine = "requests"
    blocksize = "32MB"
    if "--limit" in argv:
        try:
            idx = argv.index("--limit") + 1
            limit = int(argv[idx])
        except (ValueError, IndexError):
            logging.error("Invalid --limit value provided")
            return 1
    if "--engine" in argv:
        try:
            idx = argv.index("--engine") + 1
            engine = argv[idx]
        except IndexError:
            logging.error("Invalid --engine value provided")
            return 1
    if "--blocksize" in argv:
        try:
            idx = argv.index("--blocksize") + 1
            blocksize = argv[idx]
        except IndexError:
            logging.error("Invalid --blocksize value provided")
            return 1

    config = DownloadConfig(limit=limit, app_token=app_token, engine=engine, blocksize=blocksize)
    downloader = DatasetDownloader(config)
    downloader.download()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
