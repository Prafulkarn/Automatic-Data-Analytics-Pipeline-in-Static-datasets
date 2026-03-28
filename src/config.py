from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "output"
LOG_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "data" / "hospital_analytics.db"

PATIENT_SOURCE_PATH = RAW_DIR / "patient_master.csv"
ADMISSION_SOURCE_PATH = RAW_DIR / "admissions.csv"
TREATMENT_SOURCE_PATH = RAW_DIR / "treatments.csv"
