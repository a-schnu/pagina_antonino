from __future__ import annotations

from pathlib import Path

import pandas as pd

from analytics.metrics import renewable_dominance_pct


def build_weekly_report(df_15m: pd.DataFrame, output_dir: str = "reports") -> Path:
    base = df_15m.copy()
    base["date"] = pd.to_datetime(base["timestamp"]).dt.date

    totals = base[["generation_total_MW", "generation_solar_MW", "generation_wind_MW"]].sum()
    renewables = (base["generation_solar_MW"] + base["generation_wind_MW"] + base["generation_hydro_MW"]).sum()
    renewable_share = renewables / max(totals["generation_total_MW"], 1)

    peak_idx = base["generation_total_MW"].idxmax()
    peak_row = base.loc[peak_idx]

    report = f"""# Sicily Energy Observatory - Weekly Report

- Total electricity generation (MWh-equivalent average-based): **{totals['generation_total_MW']:.2f}**
- Renewable share: **{renewable_share:.2%}**
- Solar contribution (MW sum): **{totals['generation_solar_MW']:.2f}**
- Wind contribution (MW sum): **{totals['generation_wind_MW']:.2f}**
- Peak production timestamp: **{peak_row['timestamp']}**
- Peak production value (MW): **{peak_row['generation_total_MW']:.2f}**
- Renewable dominance metric: **{renewable_dominance_pct(base):.2%}**
"""

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = out_dir / f"weekly_report_{pd.Timestamp.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
    filename.write_text(report, encoding="utf-8")
    return filename
