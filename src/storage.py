import sqlite3

import pandas as pd


def initialize_database(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id TEXT PRIMARY KEY,
            run_started_at TEXT NOT NULL,
            run_ended_at TEXT NOT NULL,
            status TEXT NOT NULL,
            source_rows INTEGER NOT NULL,
            curated_rows INTEGER NOT NULL,
            aggregated_rows INTEGER NOT NULL,
            duration_seconds REAL NOT NULL,
            error_message TEXT
        )
        """
    )
    conn.commit()


def save_curated_data(
    db_path: str,
    patients_df: pd.DataFrame,
    curated_df: pd.DataFrame,
    aggregated_df: pd.DataFrame,
) -> None:
    """Load transformed data into SQLite warehouse tables."""
    with sqlite3.connect(db_path) as conn:
        initialize_database(conn)
        patients_df.to_sql("dim_patient", conn,
                           if_exists="replace", index=False)
        curated_df.to_sql("fact_hospital_visits", conn,
                          if_exists="replace", index=False)
        aggregated_df.to_sql("agg_daily_hospital_kpi", conn,
                             if_exists="replace", index=False)


def log_pipeline_run(db_path: str, run_record: dict) -> None:
    """Persist run metadata for monitoring and auditability."""
    with sqlite3.connect(db_path) as conn:
        initialize_database(conn)
        conn.execute(
            """
            INSERT INTO pipeline_runs (
                run_id,
                run_started_at,
                run_ended_at,
                status,
                source_rows,
                curated_rows,
                aggregated_rows,
                duration_seconds,
                error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_record["run_id"],
                run_record["run_started_at"],
                run_record["run_ended_at"],
                run_record["status"],
                run_record["source_rows"],
                run_record["curated_rows"],
                run_record["aggregated_rows"],
                run_record["duration_seconds"],
                run_record.get("error_message"),
            ),
        )
        conn.commit()
