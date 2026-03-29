"""
run_scheduler.py  (updated)
---------------------------
Runs the pipeline on a schedule AND generates fresh new data
before each run so your output files keep growing.

Usage:
  python run_scheduler.py --demo       # every 1 minute (for testing)
  python run_scheduler.py              # daily at 02:00 (production)
"""

import argparse
import time

import schedule

from src.pipeline import run_pipeline
from data_generator import append_new_data


def run_with_fresh_data(num_new_visits: int = 3):
    """Append new visits to CSVs, then run the full pipeline."""
    import datetime
    print(f"\n{'='*50}")
    print(f"Scheduler triggered at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Add new random visits before each pipeline run
    append_new_data(num_new_visits=num_new_visits)

    # Now run the pipeline — it will pick up the updated CSVs
    run_pipeline()


def main():
    parser = argparse.ArgumentParser(description="Run hospital pipeline on a schedule")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run every 1 minute for demonstration instead of daily at 02:00",
    )
    parser.add_argument(
        "--new-visits",
        type=int,
        default=3,
        help="How many new visits to generate per run (default: 3)",
    )
    args = parser.parse_args()

    # Wrap the function so the argument is passed correctly
    def job():
        run_with_fresh_data(num_new_visits=args.new_visits)

    if args.demo:
        schedule.every(10).seconds.do(job)
        print("Scheduler started in demo mode (every 1 minute)")
        print(f"Adding {args.new_visits} new visits per run")
    else:
        schedule.every().day.at("02:00").do(job)
        print("Scheduler started in production mode (daily at 02:00)")

    # Run once immediately on start
    job()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()