from __future__ import annotations

import pandas as pd
import dask.dataframe as dd

from src.processing.dask_etl import clean


def test_dask_clean_produces_peak_hour_flags() -> None:
    pdf = pd.DataFrame(
        {
            "fromhour": pd.to_datetime([
                "2024-01-01 08:00:00",
                "2024-01-01 09:00:00",
                "2024-01-01 10:00:00",
            ]),
            "tohour": pd.to_datetime([
                "2024-01-01 09:00:00",
                "2024-01-01 10:00:00",
                "2024-01-01 11:00:00",
            ]),
            "vehiclecount": [1800, 2200, 1500],
            "borough": ["Manhattan"] * 3,
            "roadwayname": ["FDR Drive"] * 3,
            "direction": ["NB"] * 3,
        }
    )
    ddf = dd.from_pandas(pdf, npartitions=1)
    transformed = clean(ddf).compute()
    assert "is_peak_hour" in transformed.columns
    assert transformed["is_peak_hour"].any()
    assert (transformed["borough"] == "MANHATTAN").all()

