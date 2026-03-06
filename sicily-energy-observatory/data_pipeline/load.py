from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


def init_db(db_path: str) -> None:
    con = duckdb.connect(db_path)
    schema_path = Path(__file__).resolve().parents[1] / "database" / "schema.sql"
    con.execute(schema_path.read_text(encoding="utf-8"))
    con.close()


def upsert_by_timestamp(con: duckdb.DuckDBPyConnection, table_name: str, df: pd.DataFrame) -> None:
    temp_name = f"tmp_{table_name}"
    con.register(temp_name, df)
    con.execute(f"DELETE FROM {table_name} USING {temp_name} t WHERE {table_name}.timestamp = t.timestamp")
    cols = ", ".join(df.columns)
    con.execute(f"INSERT INTO {table_name} ({cols}) SELECT {cols} FROM {temp_name}")


def upsert_by_date(con: duckdb.DuckDBPyConnection, table_name: str, df: pd.DataFrame) -> None:
    temp_name = f"tmp_{table_name}"
    con.register(temp_name, df)
    con.execute(f"DELETE FROM {table_name} USING {temp_name} t WHERE {table_name}.date = t.date")
    cols = ", ".join(df.columns)
    con.execute(f"INSERT INTO {table_name} ({cols}) SELECT {cols} FROM {temp_name}")


def load_all(db_path: str, raw_15m: pd.DataFrame, hourly: pd.DataFrame, daily: pd.DataFrame) -> None:
    init_db(db_path)
    con = duckdb.connect(db_path)

    upsert_by_timestamp(con, "raw_generation_15min", raw_15m)
    upsert_by_timestamp(con, "generation_hourly", hourly)
    upsert_by_date(con, "generation_daily", daily)

    con.close()
