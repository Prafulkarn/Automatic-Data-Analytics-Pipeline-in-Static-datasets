from __future__ import annotations

import time
import traceback
from datetime import datetime
from uuid import uuid4

from .config import DB_PATH, OUTPUT_DIR
from .data_sources import extract_data, generate_sample_files_if_missing
from .etl import transform_hospital_data
from .logging_setup import setup_logging
from .reporting import generate_reports
from .storage import log_pipeline_run, save_curated_data


def run_pipeline() -> dict:
    """Run one end-to-end hospital analytics pipeline execution."""
    logger = setup_logging()
    run_id = str(uuid4())
    started_at = datetime.utcnow()
    start_timer = time.perf_counter()

    source_rows = 0
    curated_rows = 0
    aggregated_rows = 0
    status = "failed"
    error_message = None
    report_paths: dict[str, str] = {}

    logger.info("Pipeline run started | run_id=%s", run_id)

    try:
        generate_sample_files_if_missing()
        admissions_df, treatments_df, patients_df = extract_data()
        source_rows = len(admissions_df) + len(treatments_df)

        curated_df, aggregated_df = transform_hospital_data(
            admissions_df, treatments_df, patients_df
        )
        curated_rows = len(curated_df)
        aggregated_rows = len(aggregated_df)

        save_curated_data(str(DB_PATH), patients_df, curated_df, aggregated_df)
        report_paths = generate_reports(aggregated_df, OUTPUT_DIR)
        status = "success"

        logger.info(
            "Pipeline transformation completed | source_rows=%s curated_rows=%s aggregated_rows=%s",
            source_rows,
            curated_rows,
            aggregated_rows,
        )
    except Exception as exc:
        error_message = str(exc)
        logger.error("Pipeline failed: %s", error_message)
        logger.debug(traceback.format_exc())
    finally:
        ended_at = datetime.utcnow()
        duration_seconds = round(time.perf_counter() - start_timer, 3)

        run_record = {
            "run_id": run_id,
            "run_started_at": started_at.isoformat(timespec="seconds"),
            "run_ended_at": ended_at.isoformat(timespec="seconds"),
            "status": status,
            "source_rows": source_rows,
            "curated_rows": curated_rows,
            "aggregated_rows": aggregated_rows,
            "duration_seconds": duration_seconds,
            "error_message": error_message,
        }
        log_pipeline_run(str(DB_PATH), run_record)

        logger.info(
            "Pipeline run finished | run_id=%s status=%s duration_seconds=%s",
            run_id,
            status,
            duration_seconds,
        )

    return {
        "run_id": run_id,
        "status": status,
        "source_rows": source_rows,
        "curated_rows": curated_rows,
        "aggregated_rows": aggregated_rows,
        "reports": report_paths,
        "error_message": error_message,
    }
