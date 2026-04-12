import argparse
import time

import schedule

from src.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run hospital pipeline on a schedule")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run every 1 minute for demonstration instead of daily at 02:00",
    )
    parser.add_argument(
        "--refresh-sample-data",
        action="store_true",
        help="Regenerate sample raw CSV data before each scheduled execution",
    )
    parser.add_argument(
        "--sample-seed",
        type=int,
        default=None,
        help="Optional random seed for sample data generation",
    )
    args = parser.parse_args()

    def _run_job() -> None:
        run_pipeline(
            refresh_sample_data=args.refresh_sample_data,
            sample_seed=args.sample_seed,
        )

    if args.demo:
        schedule.every(1).minutes.do(_run_job)
        print("Scheduler started in demo mode (every 1 minute)")
    else:
        schedule.every().day.at("02:00").do(_run_job)
        print("Scheduler started in production mode (daily at 02:00)")

    _run_job()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
