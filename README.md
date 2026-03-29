# Hospital Analytics Pipeline (Python)

This project implements an end-to-end automated analytics pipeline for a **hospital organization**.
It is intentionally simple, but includes all required enterprise pipeline components.

## 1) Data Sources

The pipeline combines multiple real-world style hospital sources:

- **Patient master (CSV):** `data/raw/patient_master.csv`
  - Patient demographics and location.
- **Admissions (CSV):** `data/raw/admissions.csv`
  - Visit-level operational records (timestamps, department, diagnosis).
- **Treatments (CSV):** `data/raw/treatments.csv`
  - Visit-level treatment and billing records.

If source files are missing, the pipeline auto-generates sample data for reproducible testing.

## 2) ETL Process

### Extract

- Reads all three CSV files into pandas DataFrames.
- Uses patient master for enrichment and joins treatments to admissions.

### Transform

- Parses datatypes and removes invalid records.
- Deduplicates visits by `visit_id`.
- Joins admissions + treatments + patients.
- Creates derived fields:
  - `bill_amount` per visit,
  - `length_of_stay_hours`,
  - `visit_date`.
- Aggregates daily hospital KPIs by date, department, and admission type.

### Load

Loads curated datasets into SQLite:

- `dim_patient`
- `fact_hospital_visits`
- `agg_daily_hospital_kpi`
- `pipeline_runs` (monitoring/audit table)

## 3) Storage Choice

- **SQLite** (`data/hospital_analytics.db`) is used as the analytical store.
- Why suitable for this project:
  - zero setup,
  - SQL querying support,
  - good for demos/small-medium workloads,
  - easy migration path later to PostgreSQL or cloud warehouses.

## 4) Scheduling Method

Two scheduling options are included:

- **In-app scheduler** using `schedule` library (`run_scheduler.py`):
  - production mode: daily at 02:00
  - demo mode: every 1 minute
- **OS scheduler (recommended in production)**:
  - Windows Task Scheduler to run `python run_pipeline.py` daily.

## 5) Logging and Monitoring

- Rotating logs are written to `logs/pipeline.log`.
- Each run stores operational metadata in `pipeline_runs` table:
  - run id, start/end time, status,
  - source/curated/aggregated row counts,
  - duration,
  - error message (if failed).

This enables historical monitoring and pipeline health checks.

## 6) Report Generation

After each successful run, reports are generated in `data/output/`:

- `daily_hospital_summary.csv` (tabular KPI output)
- `daily_patient_volume.png` (daily visit trend)
- `hospital_executive_report.md` (human-readable business summary)

## Project Structure

```text
.
|-- data/
|   |-- raw/
|   |-- output/
|   `-- hospital_analytics.db (generated)
|-- logs/
|   `-- pipeline.log (generated)
|-- src/
|   |-- config.py
|   |-- data_sources.py
|   |-- etl.py
|   |-- logging_setup.py
|   |-- pipeline.py
|   |-- reporting.py
|   `-- storage.py
|-- run_pipeline.py
|-- run_scheduler.py
`-- requirements.txt
```

## Setup and Run

1. Create environment and install dependencies:

```powershell
python3 -m venv .venv
source .venv/bin/activate//mac
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run one full pipeline execution:

```powershell
python run_pipeline.py
```

3. Run scheduler (demo mode every minute):

```powershell
python run_scheduler.py --demo


//remove database


 sqlite3 data/hospital_analytics.db
.mode column
.headers on




```

## Expected Outcome

After running, you will have:

- cleaned and aggregated hospital analytics data in SQLite,
- execution logs and monitoring metadata,
- automatically generated KPI reports for operations and management.
