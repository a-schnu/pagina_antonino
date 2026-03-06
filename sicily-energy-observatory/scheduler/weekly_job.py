from __future__ import annotations

from data_pipeline.pipeline import run_weekly_pipeline


if __name__ == "__main__":
    result = run_weekly_pipeline()
    print("Weekly job completed:", result)
    print("Set this with cron to run once per week, e.g.:")
    print("0 6 * * 1 cd /path/to/sicily-energy-observatory && /path/to/python -m scheduler.weekly_job")
