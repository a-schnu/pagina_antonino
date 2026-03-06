from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = str(BASE_DIR / "data" / "sicily_energy.duckdb")

st.set_page_config(page_title="Sicily Energy Observatory", layout="wide")
st.title("⚡ Sicily Energy Observatory")
st.caption("15-minute electricity generation monitoring, analytics, and renewable insights.")


@st.cache_data(ttl=300)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    con = duckdb.connect(DB_PATH, read_only=True)
    ts = con.execute("SELECT * FROM raw_generation_15min ORDER BY timestamp").fetchdf()
    daily = con.execute("SELECT * FROM generation_daily ORDER BY date").fetchdf()
    con.close()
    return ts, daily


try:
    ts, daily = load_data()
except Exception:
    st.warning("No database found yet. Run `python -m data_pipeline.pipeline` first.")
    st.stop()

if ts.empty:
    st.warning("No timeseries data available.")
    st.stop()

st.subheader("15-minute generation timeline")
long_ts = ts.melt(
    id_vars=["timestamp"],
    value_vars=["generation_solar_MW", "generation_wind_MW", "generation_hydro_MW", "generation_gas_MW"],
    var_name="source",
    value_name="MW",
)
fig_stack = px.area(long_ts, x="timestamp", y="MW", color="source", title="Generation by source (15-min)")
st.plotly_chart(fig_stack, use_container_width=True)

c1, c2 = st.columns(2)

with c1:
    st.subheader("Daily generation curves")
    fig_daily = px.line(
        daily,
        x="date",
        y=["generation_total_MW", "generation_solar_MW", "generation_wind_MW", "generation_hydro_MW"],
        title="Daily average generation",
    )
    st.plotly_chart(fig_daily, use_container_width=True)

with c2:
    st.subheader("Renewable share over time")
    fig_share = px.line(daily, x="date", y="renewables_share", title="Renewable share")
    fig_share.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_share, use_container_width=True)

st.subheader("Peak generation periods")
peak_cols = ["date", "peak_timestamp", "peak_generation_MW"]
st.dataframe(daily[peak_cols].sort_values("date", ascending=False).head(15), use_container_width=True)

st.subheader("Energy mix composition")
latest = daily.sort_values("date").tail(1)
if not latest.empty:
    pie_df = pd.DataFrame(
        {
            "source": ["Solar", "Wind", "Hydro", "Fossil"],
            "MW": [
                float(latest["generation_solar_MW"].iloc[0]),
                float(latest["generation_wind_MW"].iloc[0]),
                float(latest["generation_hydro_MW"].iloc[0]),
                float(latest["generation_fossil_MW"].iloc[0]),
            ],
        }
    )
    fig_mix = px.pie(pie_df, names="source", values="MW", title="Latest daily mix")
    st.plotly_chart(fig_mix, use_container_width=True)
