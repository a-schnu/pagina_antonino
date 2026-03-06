from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from analytics.anomaly_detection import detect_anomalies
from analytics.weekly_report import build_weekly_report
from data_pipeline.extract import ExtractConfig, fetch_entsoe_generation, fetch_terna_generation
from data_pipeline.load import load_all
from data_pipeline.transform import aggregate_daily, aggregate_hourly, standardize_raw

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = str(BASE_DIR / "data" / "sicily_energy.duckdb")


def run_weekly_pipeline() -> dict:
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=7)
    config = ExtractConfig(start=start, end=end)

    entsoe_df = fetch_entsoe_generation(config)
    terna_df = fetch_terna_generation(config)

    raw = pd.concat([entsoe_df, terna_df], ignore_index=True)
    if raw.empty:
        raise RuntimeError("No data returned from sources.")

    raw = standardize_raw(raw)
    hourly = aggregate_hourly(raw)
    daily = aggregate_daily(raw)

    load_all(DB_PATH, raw_15m=raw[[
        "timestamp", "region", "generation_total_MW", "generation_solar_MW", "generation_wind_MW",
        "generation_hydro_MW", "generation_gas_MW", "generation_fossil_MW", "source",
    ]], hourly=hourly[[
        "timestamp", "region", "generation_total_MW", "generation_solar_MW", "generation_wind_MW",
        "generation_hydro_MW", "generation_gas_MW", "generation_fossil_MW", "renewables_share",
    ]], daily=daily[[
        "date", "region", "generation_total_MW", "generation_solar_MW", "generation_wind_MW",
        "generation_hydro_MW", "generation_gas_MW", "generation_fossil_MW", "renewables_share",
        "peak_timestamp", "peak_generation_MW", "renewable_dominance_pct",
    ]])

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "raw").mkdir(exist_ok=True)
    (DATA_DIR / "processed").mkdir(exist_ok=True)

    raw.to_parquet(DATA_DIR / "raw" / "generation_15m_latest.parquet", index=False)
    hourly.to_parquet(DATA_DIR / "processed" / "generation_hourly_latest.parquet", index=False)
    daily.to_parquet(DATA_DIR / "processed" / "generation_daily_latest.parquet", index=False)

    anomaly_df = detect_anomalies(raw)
    anomaly_df.to_parquet(DATA_DIR / "processed" / "generation_15m_anomalies.parquet", index=False)

    report_path = build_weekly_report(raw, output_dir=str(BASE_DIR / "reports"))

    return {
        "raw_rows": len(raw),
        "hourly_rows": len(hourly),
        "daily_rows": len(daily),
        "report_path": str(report_path),
        "db_path": DB_PATH,
    }


if __name__ == "__main__":
    result = run_weekly_pipeline()
    print("Pipeline completed:", result)
