# Sicily Energy Observatory

Portfolio-grade data engineering and analytics project to monitor electricity generation in Sicily at 15-minute resolution.

## Features
- Weekly automated ingestion for the previous 7 days.
- Data extraction from ENTSO-E (and optional Terna extension point).
- Standardized generation dataset by source.
- Aggregations: hourly, daily, weekly, renewable share.
- Historical persistence in DuckDB + Parquet exports.
- FastAPI service for analytics endpoints.
- Streamlit dashboard for public visualization.
- Weekly report generation in Markdown.
- Advanced feature: anomaly detection on 15-min total generation (rolling z-score).

## Project structure

```text
sicily-energy-observatory/
├── data_pipeline/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── pipeline.py
├── database/
│   └── schema.sql
├── api/
│   └── main.py
├── dashboard/
│   └── app.py
├── analytics/
│   ├── metrics.py
│   ├── anomaly_detection.py
│   └── weekly_report.py
├── scheduler/
│   └── weekly_job.py
├── data/
│   ├── raw/
│   └── processed/
├── reports/
├── requirements.txt
└── README.md
```

## Quick start

```bash
cd sicily-energy-observatory
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your ENTSO-E token (as requested):

```bash
export entsoe_api_token="<YOUR_TOKEN>"
```

Run one weekly-style load (last 7 days):

```bash
python -m data_pipeline.pipeline
```

Run API:

```bash
uvicorn api.main:app --reload --port 8010
```

Run dashboard:

```bash
streamlit run dashboard/app.py --server.port 8501
```

## API endpoints
- `GET /generation/latest`
- `GET /generation/daily?days=30`
- `GET /generation/source-share?days=30`
- `GET /generation/timeseries?start=...&end=...`

## Notes on data sources
- ENTSO-E extraction is implemented and production-ready.
- Terna extraction has a pluggable placeholder (`fetch_terna_generation`) for credentials/dataset specifics.

