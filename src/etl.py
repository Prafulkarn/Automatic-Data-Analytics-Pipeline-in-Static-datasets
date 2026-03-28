import pandas as pd


def transform_hospital_data(
    admissions_df: pd.DataFrame, treatments_df: pd.DataFrame, patients_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Clean and aggregate hospital operational and billing records."""
    visits = admissions_df.copy()
    treatments = treatments_df.copy()
    patients = patients_df.copy()

    visits["admission_ts"] = pd.to_datetime(
        visits["admission_ts"], errors="coerce")
    visits["discharge_ts"] = pd.to_datetime(
        visits["discharge_ts"], errors="coerce")
    visits = visits.dropna(
        subset=["visit_id", "patient_id", "admission_ts", "discharge_ts", "department"])
    visits = visits[visits["discharge_ts"] >= visits["admission_ts"]]
    visits = visits.drop_duplicates(subset=["visit_id"], keep="last")

    treatments["cost"] = pd.to_numeric(treatments["cost"], errors="coerce")
    treatments = treatments.dropna(subset=["visit_id", "cost"])
    treatments = treatments[treatments["cost"] > 0]

    billing_by_visit = treatments.groupby("visit_id", as_index=False).agg(
        treatment_count=("treatment_code", "count"),
        bill_amount=("cost", "sum"),
    )
    billing_by_visit["bill_amount"] = billing_by_visit["bill_amount"].round(2)

    curated_df = visits.merge(
        patients[["patient_id", "patient_name", "gender", "age", "city"]],
        on="patient_id",
        how="left",
    ).merge(
        billing_by_visit,
        on="visit_id",
        how="left",
    )

    curated_df["patient_name"] = curated_df["patient_name"].fillna("Unknown")
    curated_df["gender"] = curated_df["gender"].fillna("Unknown")
    curated_df["city"] = curated_df["city"].fillna("Unknown")
    curated_df["age"] = pd.to_numeric(
        curated_df["age"], errors="coerce").fillna(0).astype(int)
    curated_df["treatment_count"] = curated_df["treatment_count"].fillna(
        0).astype(int)
    curated_df["bill_amount"] = curated_df["bill_amount"].fillna(0).round(2)

    curated_df["length_of_stay_hours"] = (
        (curated_df["discharge_ts"] -
         curated_df["admission_ts"]).dt.total_seconds() / 3600
    ).round(2)
    curated_df["visit_date"] = curated_df["admission_ts"].dt.date.astype(str)

    agg_df = (
        curated_df.groupby(["visit_date", "department",
                           "admission_type"], as_index=False)
        .agg(
            total_visits=("visit_id", "nunique"),
            total_treatments=("treatment_count", "sum"),
            total_bill_amount=("bill_amount", "sum"),
            avg_stay_hours=("length_of_stay_hours", "mean"),
        )
        .sort_values(["visit_date", "department", "admission_type"])
    )

    agg_df["total_bill_amount"] = agg_df["total_bill_amount"].round(2)
    agg_df["avg_stay_hours"] = agg_df["avg_stay_hours"].round(2)
    return curated_df, agg_df
