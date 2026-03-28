from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def generate_reports(aggregated_df: pd.DataFrame, output_dir: Path) -> dict:
    """Build CSV, chart, and markdown summary for stakeholders."""
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "daily_hospital_summary.csv"
    chart_path = output_dir / "daily_patient_volume.png"
    markdown_path = output_dir / "hospital_executive_report.md"

    aggregated_df.to_csv(csv_path, index=False)

    visits_by_date = (
        aggregated_df.groupby("visit_date", as_index=False)[
            "total_visits"].sum()
    )
    visits_by_date["visit_date"] = pd.to_datetime(visits_by_date["visit_date"])
    visits_by_date = visits_by_date.sort_values("visit_date")

    plt.figure(figsize=(10, 5))
    plt.plot(visits_by_date["visit_date"],
             visits_by_date["total_visits"], marker="o")
    plt.title("Daily Patient Visits")
    plt.xlabel("Date")
    plt.ylabel("Visit Count")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    total_visits = int(aggregated_df["total_visits"].sum())
    total_treatments = int(aggregated_df["total_treatments"].sum())
    total_billing = float(aggregated_df["total_bill_amount"].sum())

    top_department = (
        aggregated_df.groupby("department", as_index=False)["total_visits"]
        .sum()
        .sort_values("total_visits", ascending=False)
        .head(1)
    )

    billing_by_admission_type = (
        aggregated_df.groupby("admission_type", as_index=False)[
            "total_bill_amount"]
        .sum()
        .sort_values("total_bill_amount", ascending=False)
    )

    avg_stay_hours = float(aggregated_df["avg_stay_hours"].mean())

    lines = [
        "# Hospital Analytics Executive Report",
        "",
        "## KPI Snapshot",
        f"- Total Visits: {total_visits:,}",
        f"- Total Treatments: {total_treatments:,}",
        f"- Total Billing Amount: {total_billing:,.2f}",
        f"- Average Stay (hours): {avg_stay_hours:.2f}",
    ]

    if not top_department.empty:
        lines.append(
            f"- Busiest Department: {top_department.iloc[0]['department']} ({int(top_department.iloc[0]['total_visits'])} visits)"
        )

    lines.extend(["", "## Billing by Admission Type"])

    for _, row in billing_by_admission_type.iterrows():
        lines.append(
            f"- {row['admission_type']}: {row['total_bill_amount']:.2f}")

    markdown_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "csv": str(csv_path),
        "chart": str(chart_path),
        "executive_report": str(markdown_path),
    }
