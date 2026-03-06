from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from entsoe import EntsoePandasClient

SICILY_BIDDING_ZONE = "IT-SICI"
ITALY_COUNTRY_CODE = "IT"


@dataclass
class ExtractConfig:
    start: datetime
    end: datetime
    region: str = "Sicily"


def _get_entsoe_token() -> str:
    token = os.getenv("entsoe_api_token") or os.getenv("ENTSOE_API_TOKEN")
    if not token:
        raise ValueError("Missing ENTSO-E token. Set env var 'entsoe_api_token'.")
    return token


def fetch_entsoe_generation(config: ExtractConfig) -> pd.DataFrame:
    """Fetch 15-min generation for Sicily from ENTSO-E and flatten to canonical columns."""
    client = EntsoePandasClient(api_key=_get_entsoe_token())

    start = pd.Timestamp(config.start, tz="Europe/Rome")
    end = pd.Timestamp(config.end, tz="Europe/Rome")

    try:
        raw = client.query_generation(country_code=SICILY_BIDDING_ZONE, start=start, end=end, psr_type=None)
    except Exception:
        # Some entsoe-py versions only accept 2-letter country codes in query_generation.
        # Fall back to Italy-level data to avoid hard failure, while keeping Sicily region label.
        raw = client.query_generation(country_code=ITALY_COUNTRY_CODE, start=start, end=end, psr_type=None)

    if isinstance(raw, pd.Series):
        raw = raw.to_frame("Actual Aggregated")

    raw = raw.resample("15min").mean().interpolate(limit_direction="both")

    source_map = {
        "Solar": "generation_solar_MW",
        "Wind Onshore": "generation_wind_MW",
        "Hydro Water Reservoir": "generation_hydro_MW",
        "Hydro Run-of-river and poundage": "generation_hydro_MW",
        "Fossil Gas": "generation_gas_MW",
    }

    df = pd.DataFrame(index=raw.index)
    for source, target_col in source_map.items():
        if source in raw.columns:
            if target_col not in df:
                df[target_col] = 0.0
            df[target_col] = df[target_col].fillna(0.0) + raw[source].fillna(0.0)

    for col in [
        "generation_solar_MW",
        "generation_wind_MW",
        "generation_hydro_MW",
        "generation_gas_MW",
    ]:
        if col not in df:
            df[col] = 0.0

    if "Actual Aggregated" in raw.columns:
        df["generation_total_MW"] = raw["Actual Aggregated"].fillna(method="ffill")
    else:
        df["generation_total_MW"] = (
            df["generation_solar_MW"]
            + df["generation_wind_MW"]
            + df["generation_hydro_MW"]
            + df["generation_gas_MW"]
        )

    df["generation_fossil_MW"] = (df["generation_total_MW"] - (df["generation_solar_MW"] + df["generation_wind_MW"] + df["generation_hydro_MW"]))
    df["generation_fossil_MW"] = df["generation_fossil_MW"].clip(lower=0.0)

    out = df.reset_index().rename(columns={"index": "timestamp"})
    out["timestamp"] = pd.to_datetime(out["timestamp"]).dt.tz_convert("UTC").dt.tz_localize(None)
    out["region"] = config.region
    out["source"] = "ENTSOE"

    cols = [
        "timestamp",
        "region",
        "generation_total_MW",
        "generation_solar_MW",
        "generation_wind_MW",
        "generation_hydro_MW",
        "generation_gas_MW",
        "generation_fossil_MW",
        "source",
    ]
    return out[cols].sort_values("timestamp").drop_duplicates(subset=["timestamp"], keep="last")


def fetch_terna_generation(config: ExtractConfig) -> pd.DataFrame:
    """Optional integration point for Terna datasets.

    Replace with authenticated Terna API/client implementation when credentials and endpoint are available.
    """
    return pd.DataFrame(
        columns=[
            "timestamp",
            "region",
            "generation_total_MW",
            "generation_solar_MW",
            "generation_wind_MW",
            "generation_hydro_MW",
            "generation_gas_MW",
            "generation_fossil_MW",
            "source",
        ]
    )
