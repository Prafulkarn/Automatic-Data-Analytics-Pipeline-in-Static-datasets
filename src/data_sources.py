from datetime import datetime, timedelta
from random import Random

import pandas as pd

from .config import ADMISSION_SOURCE_PATH, PATIENT_SOURCE_PATH, RAW_DIR, TREATMENT_SOURCE_PATH


def _generate_patient_master() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"patient_id": "PT001", "patient_name": "Aarav Mehta",
                "gender": "Male", "age": 45, "city": "Pune"},
            {"patient_id": "PT002", "patient_name": "Sana Khan",
                "gender": "Female", "age": 31, "city": "Mumbai"},
            {"patient_id": "PT003", "patient_name": "Rohan Iyer",
                "gender": "Male", "age": 59, "city": "Nashik"},
            {"patient_id": "PT004", "patient_name": "Priya Das",
                "gender": "Female", "age": 27, "city": "Pune"},
            {"patient_id": "PT005", "patient_name": "Anjali Rao",
                "gender": "Female", "age": 66, "city": "Nagpur"},
            {"patient_id": "PT006", "patient_name": "Vikram Shah",
                "gender": "Male", "age": 52, "city": "Mumbai"},
            {"patient_id": "PT007", "patient_name": "Neha Patil",
                "gender": "Female", "age": 38, "city": "Pune"},
            {"patient_id": "PT008", "patient_name": "Karan Gupta",
                "gender": "Male", "age": 41, "city": "Thane"},
        ]
    )


def generate_sample_files_if_missing() -> None:
    """Create sample hospital files when raw sources are not available."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rng = Random(42)

    patients_df = _generate_patient_master()
    if not PATIENT_SOURCE_PATH.exists():
        patients_df.to_csv(PATIENT_SOURCE_PATH, index=False)

    departments = ["Cardiology", "Orthopedics",
                   "Neurology", "General Medicine", "Pediatrics"]
    admission_types = ["Emergency", "Elective", "Referral"]
    diagnosis = ["Hypertension", "Fracture",
                 "Migraine", "Diabetes", "Infection"]

    if not ADMISSION_SOURCE_PATH.exists():
        admission_rows = []
        now = datetime.now()
        for i in range(1, 81):
            admit_ts = now - \
                timedelta(days=rng.randint(0, 20), hours=rng.randint(0, 23))
            los_hours = rng.randint(8, 120)
            discharge_ts = admit_ts + timedelta(hours=los_hours)
            admission_rows.append(
                {
                    "visit_id": f"VST-{i:05d}",
                    "patient_id": rng.choice(patients_df["patient_id"].tolist()),
                    "admission_ts": admit_ts.isoformat(timespec="seconds"),
                    "discharge_ts": discharge_ts.isoformat(timespec="seconds"),
                    "department": rng.choice(departments),
                    "diagnosis": rng.choice(diagnosis),
                    "admission_type": rng.choice(admission_types),
                }
            )
        pd.DataFrame(admission_rows).to_csv(ADMISSION_SOURCE_PATH, index=False)

    if not TREATMENT_SOURCE_PATH.exists():
        treatment_rows = []
        treatment_catalog = [
            ("T100", "ECG", 1200),
            ("T101", "X-Ray", 1800),
            ("T102", "MRI", 7800),
            ("T103", "Blood Panel", 900),
            ("T104", "Physiotherapy", 1500),
            ("T105", "CT Scan", 6500),
        ]

        for i in range(1, 81):
            visit_id = f"VST-{i:05d}"
            for _ in range(rng.randint(1, 3)):
                code, name, base_cost = rng.choice(treatment_catalog)
                treatment_rows.append(
                    {
                        "visit_id": visit_id,
                        "treatment_code": code,
                        "treatment_name": name,
                        "cost": round(base_cost * rng.uniform(0.9, 1.2), 2),
                        "insurance_covered": rng.choice(["yes", "no"]),
                    }
                )

        pd.DataFrame(treatment_rows).to_csv(TREATMENT_SOURCE_PATH, index=False)


def extract_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Extract admission, treatment, and patient master datasets."""
    patients_df = pd.read_csv(PATIENT_SOURCE_PATH)
    admissions_df = pd.read_csv(ADMISSION_SOURCE_PATH)
    treatments_df = pd.read_csv(TREATMENT_SOURCE_PATH)

    return admissions_df, treatments_df, patients_df
