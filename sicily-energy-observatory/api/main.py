from __future__ import annotations

from datetime import datetime
from pathlib import Path

import duckdb
from fastapi import FastAPI, Query

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = str(BASE_DIR / "data" / "sicily_energy.duckdb")

app = FastAPI(title="Sicily Energy Observatory API", version="1.0.0")


def q(sql: str):
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(sql).fetchdf()
    con.close()
    return df.to_dict(orient="records")


@app.get("/generation/latest")
def generation_latest():
    return q(
        """
        SELECT *
        FROM raw_generation_15min
        ORDER BY timestamp DESC
        LIMIT 1
        """
    )


@app.get("/generation/daily")
def generation_daily(days: int = Query(default=30, ge=1, le=3650)):
    return q(
        f"""
        SELECT *
        FROM generation_daily
        WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
        ORDER BY date
        """
    )


@app.get("/generation/source-share")
def source_share(days: int = Query(default=30, ge=1, le=3650)):
    return q(
        f"""
        SELECT
            date,
            generation_total_MW,
            (generation_solar_MW + generation_wind_MW + generation_hydro_MW) AS renewables_MW,
            generation_fossil_MW,
            renewables_share
        FROM generation_daily
        WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
        ORDER BY date
        """
    )


@app.get("/generation/timeseries")
def generation_timeseries(
    start: datetime | None = None,
    end: datetime | None = None,
):
    if start and end:
        return q(
            f"""
            SELECT *
            FROM raw_generation_15min
            WHERE timestamp BETWEEN TIMESTAMP '{start.isoformat(sep=' ')}' AND TIMESTAMP '{end.isoformat(sep=' ')}'
            ORDER BY timestamp
            """
        )
    return q(
        """
        SELECT *
        FROM raw_generation_15min
        ORDER BY timestamp DESC
        LIMIT 2000
        """
    )
