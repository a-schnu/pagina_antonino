from __future__ import annotations

import pandas as pd


def detect_anomalies(df: pd.DataFrame, window: int = 96, z_threshold: float = 3.0) -> pd.DataFrame:
    """Detect anomalies on 15-min total generation using rolling z-score.

    window=96 corresponds to 24 hours at 15-minute resolution.
    """
    out = df.copy().sort_values("timestamp")
    s = out["generation_total_MW"]
    rolling_mean = s.rolling(window=window, min_periods=window // 2).mean()
    rolling_std = s.rolling(window=window, min_periods=window // 2).std().replace(0, pd.NA)
    z = ((s - rolling_mean) / rolling_std).fillna(0.0)

    out["zscore_total_generation"] = z
    out["is_anomaly"] = z.abs() >= z_threshold
    return out
