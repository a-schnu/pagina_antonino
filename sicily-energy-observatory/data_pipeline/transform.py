from __future__ import annotations

import pandas as pd


GEN_COLS = [
    "generation_total_MW",
    "generation_solar_MW",
    "generation_wind_MW",
    "generation_hydro_MW",
    "generation_gas_MW",
    "generation_fossil_MW",
]


def standardize_raw(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=False)
    out = out.sort_values("timestamp")

    for col in GEN_COLS:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)

    out["renewables_MW"] = (
        out["generation_solar_MW"] + out["generation_wind_MW"] + out["generation_hydro_MW"]
    )
    out["renewables_share"] = (out["renewables_MW"] / out["generation_total_MW"].replace(0, pd.NA)).fillna(0.0)
    return out


def aggregate_hourly(df_15m: pd.DataFrame) -> pd.DataFrame:
    base = standardize_raw(df_15m).set_index("timestamp")
    agg = base.groupby("region")[GEN_COLS + ["renewables_MW"]].resample("1H").mean().reset_index()
    agg["renewables_share"] = (agg["renewables_MW"] / agg["generation_total_MW"].replace(0, pd.NA)).fillna(0.0)
    return agg.drop(columns=["renewables_MW"])


def aggregate_daily(df_15m: pd.DataFrame) -> pd.DataFrame:
    base = standardize_raw(df_15m).copy()
    base["date"] = base["timestamp"].dt.date

    daily = (
        base.groupby(["date", "region"], as_index=False)[GEN_COLS + ["renewables_share"]]
        .mean()
    )

    peaks = base.loc[base.groupby("date")["generation_total_MW"].idxmax(), ["date", "timestamp", "generation_total_MW"]]
    peaks = peaks.rename(columns={"timestamp": "peak_timestamp", "generation_total_MW": "peak_generation_MW"})

    dominance = (
        (base["renewables_MW"] > base["generation_fossil_MW"])
        .groupby(base["date"])
        .mean()
        .reset_index(name="renewable_dominance_pct")
    )

    out = daily.merge(peaks, on="date", how="left").merge(dominance, on="date", how="left")
    return out


def aggregate_weekly(df_15m: pd.DataFrame) -> pd.DataFrame:
    base = standardize_raw(df_15m).set_index("timestamp")
    weekly = base.groupby("region")[GEN_COLS + ["renewables_share"]].resample("1W").mean().reset_index()
    return weekly
