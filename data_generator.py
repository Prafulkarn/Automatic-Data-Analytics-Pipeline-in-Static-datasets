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
    ("T100", "ECG", 1200), ("T101", "X-Ray", 1800), ("T102", "MRI", 7800),
    ("T103", "Blood Panel", 900), ("T104", "Physiotherapy", 1500), ("T105", "CT Scan", 6500),
]

def append_new_data(num_new_visits: int = 3) -> None:
    admissions_path = RAW_DIR / "admissions.csv"
    treatments_path = RAW_DIR / "treatments.csv"
    patients_path = RAW_DIR / "patient_master.csv"

    if not patients_path.exists():
        print("[DataGenerator] patient_master.csv not found.")
        return

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

    # FIX: Correctly extract the maximum integer from visit_id
    if not existing_admissions.empty and "visit_id" in existing_admissions.columns:
        # Extract digits, convert to numeric, and get the max as a scalar integer
        numbers = existing_admissions["visit_id"].str.extract(r"(\d+)")[0].dropna().astype(int)
        last_num = int(numbers.max()) if not numbers.empty else 0
    else: 
        last_num = 0

    # NEW: Force visit count between 10 and 100
    num_new_visits = random.randint(8, 15) 
    
    print(f"[DataGenerator] Generating {num_new_visits} new visits starting from VST-{last_num+1:05d}...")

    new_admissions, new_treatments = [], []
    now = datetime.now()

    for i in range(1, num_new_visits + 1):
        visit_id = f"VST-{last_num + i:05d}"
        
        # NEW: Set random date within the last 60 days
        day_offset = random.randint(0, 1)
        hour_offset = random.randint(0, 23)
        admit_ts = now - timedelta(days=day_offset, hours=hour_offset)
        
        discharge_ts = admit_ts + timedelta(hours=max(4, min(int(random.gauss(36, 20)), 120)))

        new_admissions.append({
            "visit_id": visit_id,
            "patient_id": random.choice(patient_ids),
            "admission_ts": admit_ts.isoformat(timespec="seconds"),
            "discharge_ts": discharge_ts.isoformat(timespec="seconds"),
            "department": random.choices(DEPARTMENTS, weights=[3, 2, 2, 4, 3], k=1)[0],
            "diagnosis": random.choice(DIAGNOSES),
            "admission_type": random.choices(ADMISSION_TYPES, weights=[4, 3, 2], k=1)[0],
        })

        for _ in range(max(1, int(random.gauss(2, 1)))):
            code, name, base_cost = random.choice(TREATMENT_CATALOG)
            new_treatments.append({
                "visit_id": visit_id,
                "treatment_code": code,
                "treatment_name": name,
                "cost": round(base_cost * random.uniform(0.7, 1.5), 2),
                "insurance_covered": random.choice(["yes", "no"]),
            })

    # Append and save
    updated_admissions = pd.concat([existing_admissions, pd.DataFrame(new_admissions)], ignore_index=True)
    updated_treatments = pd.concat([existing_treatments, pd.DataFrame(new_treatments)], ignore_index=True)
    
    updated_admissions.to_csv(admissions_path, index=False)
    updated_treatments.to_csv(treatments_path, index=False)
    
    print(f"[DataGenerator] Successfully added {num_new_visits} visits.")
