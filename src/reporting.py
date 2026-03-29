from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

def generate_reports(aggregated_df: pd.DataFrame, output_dir: Path) -> dict:
    """Build CSV, chart, and markdown summary for stakeholders."""
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path      = output_dir / "daily_hospital_summary.csv"
    chart_path    = output_dir / "daily_patient_volume.png"
    markdown_path = output_dir / "hospital_executive_report.md"

    # ── Merge with existing CSV ──
    if csv_path.exists():
        existing_df = pd.read_csv(csv_path)
        combined_df = pd.concat([existing_df, aggregated_df], ignore_index=True)
        combined_df = combined_df.groupby(
            ["visit_date", "department", "admission_type"], as_index=False
        ).agg(
            total_visits      = ("total_visits", "sum"),
            total_treatments  = ("total_treatments", "sum"),
            total_bill_amount = ("total_bill_amount", "sum"),
            avg_stay_hours    = ("avg_stay_hours", "mean")
        ).sort_values(["visit_date", "department", "admission_type"])
    else:
        combined_df = aggregated_df.copy()

    combined_df.to_csv(csv_path, index=False)
    print(f"[Reporter] CSV updated — total rows: {len(combined_df)}")

    # ── Chart: Total Visits by Date ──
    visits_by_date = combined_df.groupby("visit_date", as_index=False)["total_visits"].sum()
    visits_by_date["visit_date"] = pd.to_datetime(visits_by_date["visit_date"])
    visits_by_date = visits_by_date.sort_values("visit_date")

    plt.figure(figsize=(14, 6))  # Wider and taller figure
    ax = plt.gca()

    # Dynamic y-axis interval (nice rounded step)
    max_visits = visits_by_date["total_visits"].max()
    step = max(10, int(max_visits / 10))  # divide max into 10 ticks
    ax.yaxis.set_major_locator(mticker.MultipleLocator(step))
    
    # Plot line
    ax.plot(visits_by_date["visit_date"], visits_by_date["total_visits"], 
            marker="o", linestyle="-", color="#1f77b4", label="Total Visits")
    
    # Optional: Plot bar behind line for volume effect
    ax.bar(visits_by_date["visit_date"], visits_by_date["total_visits"], 
           alpha=0.2, color="#1f77b4")

    ax.set_title("Daily Patient Visits", fontsize=16)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Visit Count", fontsize=12)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    # ── Markdown report ──
    total_visits     = int(combined_df["total_visits"].sum())
    total_treatments = int(combined_df["total_treatments"].sum())
    total_billing    = float(combined_df["total_bill_amount"].sum())
    avg_stay_hours   = float(combined_df["avg_stay_hours"].mean())

    top_department = (
        combined_df.groupby("department", as_index=False)["total_visits"]
        .sum()
        .sort_values("total_visits", ascending=False)
        .head(1)
    )

    billing_by_admission_type = (
        combined_df.groupby("admission_type", as_index=False)["total_bill_amount"]
        .sum()
        .sort_values("total_bill_amount", ascending=False)
    )

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
            f"- Busiest Department: {top_department.iloc[0]['department']} "
            f"({int(top_department.iloc[0]['total_visits'])} visits)"
        )

    lines.extend(["", "## Billing by Admission Type"])
    for _, row in billing_by_admission_type.iterrows():
        lines.append(f"- {row['admission_type']}: {row['total_bill_amount']:.2f}")

    markdown_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "csv":              str(csv_path),
        "chart":            str(chart_path),
        "executive_report": str(markdown_path),
    }