import sqlite3

import pandas as pd


def initialize_database(conn: sqlite3.Connection) -> None:
    conn.execute("""
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
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dim_patient (
            patient_id TEXT PRIMARY KEY,
            patient_name TEXT,
            gender TEXT,
            age INTEGER,
            city TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fact_hospital_visits (
            visit_id TEXT PRIMARY KEY,
            patient_id TEXT,
            admission_ts TEXT,
            discharge_ts TEXT,
            department TEXT,
            diagnosis TEXT,
            admission_type TEXT,
            patient_name TEXT,
            gender TEXT,
            age INTEGER,
            city TEXT,
            treatment_count INTEGER,
            bill_amount REAL,
            length_of_stay_hours REAL,
            visit_date TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agg_daily_hospital_kpi (
            visit_date TEXT,
            department TEXT,
            admission_type TEXT,
            total_visits INTEGER,
            total_treatments INTEGER,
            total_bill_amount REAL,
            avg_stay_hours REAL,
            PRIMARY KEY (visit_date, department, admission_type)
        )
    """)
    conn.commit()


def _str(value):
    """Convert any value to a SQLite-safe type — converts Timestamps to strings."""
    if pd.isnull(value) if not isinstance(value, (list, dict)) else False:
        return None
    if hasattr(value, 'isoformat'):   # catches pandas Timestamp and datetime
        return value.isoformat()
    return value


def save_curated_data(
    db_path: str,
    patients_df: pd.DataFrame,
    curated_df: pd.DataFrame,
    aggregated_df: pd.DataFrame,
) -> None:
    """Load transformed data into SQLite warehouse tables — appending new rows only."""
    with sqlite3.connect(db_path) as conn:
        initialize_database(conn)

        # Patients — insert or ignore if patient_id already exists
        for _, row in patients_df.iterrows():
            conn.execute("""
                INSERT OR IGNORE INTO dim_patient
                    (patient_id, patient_name, gender, age, city)
                VALUES (?, ?, ?, ?, ?)
            """, (
                _str(row.get("patient_id")),
                _str(row.get("patient_name")),
                _str(row.get("gender")),
                _str(row.get("age")),
                _str(row.get("city")),
            ))

        # Visits — insert or ignore if visit_id already exists
        for _, row in curated_df.iterrows():
            conn.execute("""
                INSERT OR IGNORE INTO fact_hospital_visits (
                    visit_id, patient_id, admission_ts, discharge_ts,
                    department, diagnosis, admission_type,
                    patient_name, gender, age, city,
                    treatment_count, bill_amount,
                    length_of_stay_hours, visit_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                _str(row.get("visit_id")),
                _str(row.get("patient_id")),
                _str(row.get("admission_ts")),    # Timestamp → string
                _str(row.get("discharge_ts")),    # Timestamp → string
                _str(row.get("department")),
                _str(row.get("diagnosis")),
                _str(row.get("admission_type")),
                _str(row.get("patient_name")),
                _str(row.get("gender")),
                _str(row.get("age")),
                _str(row.get("city")),
                _str(row.get("treatment_count")),
                _str(row.get("bill_amount")),
                _str(row.get("length_of_stay_hours")),
                _str(row.get("visit_date")),
            ))

        # KPI aggregation — update if same date+dept+type exists, insert if new
        for _, row in aggregated_df.iterrows():
            conn.execute("""
                INSERT INTO agg_daily_hospital_kpi
                    (visit_date, department, admission_type,
                     total_visits, total_treatments, total_bill_amount, avg_stay_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(visit_date, department, admission_type)
                DO UPDATE SET
                    total_visits      = excluded.total_visits,
                    total_treatments  = excluded.total_treatments,
                    total_bill_amount = excluded.total_bill_amount,
                    avg_stay_hours    = excluded.avg_stay_hours
            """, (
                _str(row["visit_date"]),
                _str(row["department"]),
                _str(row["admission_type"]),
                _str(row["total_visits"]),
                _str(row["total_treatments"]),
                _str(row["total_bill_amount"]),
                _str(row["avg_stay_hours"]),
            ))

        conn.commit()


def log_pipeline_run(db_path: str, run_record: dict) -> None:
    """Persist run metadata for monitoring and auditability."""
    with sqlite3.connect(db_path) as conn:
        initialize_database(conn)
        conn.execute("""
            INSERT INTO pipeline_runs (
                run_id, run_started_at, run_ended_at, status,
                source_rows, curated_rows, aggregated_rows,
                duration_seconds, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_record["run_id"],
            run_record["run_started_at"],
            run_record["run_ended_at"],
            run_record["status"],
            run_record["source_rows"],
            run_record["curated_rows"],
            run_record["aggregated_rows"],
            run_record["duration_seconds"],
            run_record.get("error_message"),
        ))
        conn.commit()