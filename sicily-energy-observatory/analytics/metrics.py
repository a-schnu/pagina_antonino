from __future__ import annotations

import pandas as pd


def renewable_penetration(df: pd.DataFrame) -> pd.Series:
    renewables = df["generation_solar_MW"] + df["generation_wind_MW"] + df["generation_hydro_MW"]
    return (renewables / df["generation_total_MW"].replace(0, pd.NA)).fillna(0.0)


def renewable_dominance_pct(df: pd.DataFrame) -> float:
    renewables = df["generation_solar_MW"] + df["generation_wind_MW"] + df["generation_hydro_MW"]
    dominance = (renewables > df["generation_fossil_MW"]).mean()
    return float(dominance)


def peak_generation_periods(df: pd.DataFrame) -> pd.DataFrame:
    base = df.copy()
    base["date"] = pd.to_datetime(base["timestamp"]).dt.date
    idx = base.groupby("date")["generation_total_MW"].idxmax()
    return base.loc[idx, ["date", "timestamp", "generation_total_MW"]].sort_values("date")
