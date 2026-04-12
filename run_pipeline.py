import argparse

from src.pipeline import run_pipeline


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run hospital analytics pipeline")
    parser.add_argument(
        "--refresh-sample-data",
        action="store_true",
        help="Regenerate sample raw CSV data before executing the pipeline",
    )
    parser.add_argument(
        "--sample-seed",
        type=int,
        default=None,
        help="Optional random seed for sample data generation",
    )
    args = parser.parse_args()

    result = run_pipeline(
        refresh_sample_data=args.refresh_sample_data,
        sample_seed=args.sample_seed,
    )
    print("Pipeline execution summary")
    print(f"run_id: {result['run_id']}")
    print(f"status: {result['status']}")
    print(f"source_rows: {result['source_rows']}")
    print(f"curated_rows: {result['curated_rows']}")
    print(f"aggregated_rows: {result['aggregated_rows']}")

    if result["reports"]:
        print("Generated reports:")
        for name, path in result["reports"].items():
            print(f"- {name}: {path}")

    if result["error_message"]:
        print(f"error: {result['error_message']}")
