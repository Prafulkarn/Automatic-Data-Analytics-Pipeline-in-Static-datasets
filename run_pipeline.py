from src.pipeline import run_pipeline


if __name__ == "__main__":
    result = run_pipeline()
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
