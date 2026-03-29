from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

def generate_reports(aggregated_df: pd.DataFrame, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "daily_hospital_summary.csv"
    chart_path = output_dir / "daily_patient_volume.png"

    # Standard aggregation logic for CSV
    if csv_path.exists():
        existing_df = pd.read_csv(csv_path)
        combined_df = pd.concat([existing_df, aggregated_df], ignore_index=True)
        combined_df = combined_df.groupby(["visit_date", "department", "admission_type"], as_index=False).agg(
            total_visits=("total_visits", "sum"),
            total_treatments=("total_treatments", "sum"),
            total_bill_amount=("total_bill_amount", "sum"),
            avg_stay_hours=("avg_stay_hours", "mean")
        ).sort_values("visit_date")
    else:
        combined_df = aggregated_df.copy()

    combined_df.to_csv(csv_path, index=False)

    # ── Chart: Fixed 10-100 scale ──
    visits_by_date = combined_df.groupby("visit_date")["total_visits"].sum().reset_index()
    visits_by_date["visit_date"] = pd.to_datetime(visits_by_date["visit_date"])

    plt.figure(figsize=(14, 6))
    ax = plt.gca()

    # NEW: Force Y-axis to show 0 to 110 for better 100-visit visibility
    ax.set_ylim(0, 110) 
    ax.yaxis.set_major_locator(mticker.MultipleLocator(10))

    ax.plot(visits_by_date["visit_date"], visits_by_date["total_visits"], marker="o", color="#1f77b4")
    ax.bar(visits_by_date["visit_date"], visits_by_date["total_visits"], alpha=0.2, color="#1f77b4")

    ax.set_title("Daily Patient Visits (Last 60 Days)", fontsize=16)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return {"csv": str(csv_path), "chart": str(chart_path)}
