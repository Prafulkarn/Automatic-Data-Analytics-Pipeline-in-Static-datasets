"""
data_generator.py
-----------------
Drop this file into your project root.
It appends fresh new visits and treatments to your CSV files
on every scheduler run, so your data keeps growing with realistic randomness.
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# ── Config ──
RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

DEPARTMENTS = ["Cardiology", "Orthopedics", "Neurology", "General Medicine", "Pediatrics"]
ADMISSION_TYPES = ["Emergency", "Elective", "Referral"]
DIAGNOSES = ["Hypertension", "Fracture", "Migraine", "Diabetes", "Infection"]
TREATMENT_CATALOG = [
    ("T100", "ECG", 1200),
    ("T101", "X-Ray", 1800),
    ("T102", "MRI", 7800),
    ("T103", "Blood Panel", 900),
    ("T104", "Physiotherapy", 1500),
    ("T105", "CT Scan", 6500),
]


def append_new_data(num_new_visits: int = 3) -> None:
    """Append new hospital visits and treatments with realistic randomness."""
    admissions_path = RAW_DIR / "admissions.csv"
    treatments_path = RAW_DIR / "treatments.csv"
    patients_path = RAW_DIR / "patient_master.csv"

    if not patients_path.exists():
        print("[DataGenerator] patient_master.csv not found. Run pipeline once first.")
        return

    # ── Load patient master and previous admissions/treatments ──
    patients_df = pd.read_csv(patients_path)
    patient_ids = patients_df["patient_id"].tolist()

    try:
        existing_admissions = pd.read_csv(admissions_path)
    except:
        existing_admissions = pd.DataFrame()

    try:
        existing_treatments = pd.read_csv(treatments_path)
    except:
        existing_treatments = pd.DataFrame()

    # ── Determine last visit number ──
    if not existing_admissions.empty and "visit_id" in existing_admissions.columns:
        numbers = (
            existing_admissions["visit_id"]
            .dropna()
            .str.extract(r"(\d+)")[0]
            .dropna()
            .astype(int)
        )
        last_num = numbers.max() if not numbers.empty else 0
    else:
        last_num = 0

    # ── Daily multiplier for realistic spikes ──
    daily_multiplier = random.choice([0.5, 1, 1, 2, 3])
    num_new_visits = max(1, int(num_new_visits * daily_multiplier))

    print(f"[DataGenerator] Last visit: VST-{last_num:05d} | Generating {num_new_visits} new visits...")

    new_admissions = []
    new_treatments = []
    now = datetime.now()

    for i in range(1, num_new_visits + 1):
        visit_num = last_num + i
        visit_id = f"VST-{visit_num:05d}"
        patient_id = random.choice(patient_ids)

        # ── Realistic timestamps ──
        day_offset = random.randint(0, 10)  # past 10 days
        hour_offset = random.randint(0, 23)

        admit_ts = now - timedelta(days=day_offset, hours=hour_offset)
        stay_hours = int(random.gauss(36, 20))  # normal distribution
        stay_hours = max(4, min(stay_hours, 120))  # clamp 4–120 hrs
        discharge_ts = admit_ts + timedelta(hours=stay_hours)

        # ── Department and admission type bias ──
        department = random.choices(
            DEPARTMENTS,
            weights=[3, 2, 2, 4, 3],  # General Medicine busiest
            k=1
        )[0]

        admission_type = random.choices(
            ADMISSION_TYPES,
            weights=[4, 3, 2],  # Emergency more frequent
            k=1
        )[0]

        diagnosis = random.choice(DIAGNOSES)

        new_admissions.append({
            "visit_id": visit_id,
            "patient_id": patient_id,
            "admission_ts": admit_ts.isoformat(timespec="seconds"),
            "discharge_ts": discharge_ts.isoformat(timespec="seconds"),
            "department": department,
            "diagnosis": diagnosis,
            "admission_type": admission_type,
        })

        # ── Treatments (1–3, normally distributed) ──
        num_treatments = max(1, int(random.gauss(2, 1)))
        for _ in range(num_treatments):
            code, name, base_cost = random.choice(TREATMENT_CATALOG)
            new_treatments.append({
                "visit_id": visit_id,
                "treatment_code": code,
                "treatment_name": name,
                "cost": round(base_cost * random.uniform(0.7, 1.5), 2),  # wider variability
                "insurance_covered": random.choice(["yes", "no"]),
            })

    # ── Append to existing CSVs ──
    updated_admissions = pd.concat([existing_admissions, pd.DataFrame(new_admissions)], ignore_index=True)
    updated_treatments = pd.concat([existing_treatments, pd.DataFrame(new_treatments)], ignore_index=True)

    updated_admissions.to_csv(admissions_path, index=False)
    updated_treatments.to_csv(treatments_path, index=False)

    print(f"[DataGenerator] Added VST-{last_num+1:05d} to VST-{last_num+num_new_visits:05d} "
          f"| Total admissions: {len(updated_admissions)} "
          f"| Total treatments: {len(updated_treatments)}")