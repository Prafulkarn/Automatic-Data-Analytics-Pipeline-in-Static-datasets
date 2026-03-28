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
    args = parser.parse_args()

    if args.demo:
        schedule.every(1).minutes.do(run_pipeline)
        print("Scheduler started in demo mode (every 1 minute)")
    else:
        schedule.every().day.at("02:00").do(run_pipeline)
        print("Scheduler started in production mode (daily at 02:00)")

    run_pipeline()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
