from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import DB_PATH, OUTPUT_DIR
from src.pipeline import run_pipeline


st.set_page_config(
    page_title="Hospital Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
)


def _db_exists() -> bool:
    return Path(DB_PATH).exists()


@st.cache_data(ttl=60)
def load_table(table_name: str) -> pd.DataFrame:
    if not _db_exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)


def load_report_markdown() -> str:
    report_path = OUTPUT_DIR / "hospital_executive_report.md"
    if report_path.exists():
        return report_path.read_text(encoding="utf-8")
    return "Executive report not found yet. Run pipeline to generate it."


def render_header() -> None:
    st.title("Hospital Analytics Dashboard")
    st.caption("Interactive view over pipeline outputs and monitoring metadata.")


def render_controls() -> None:
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Run Pipeline Now", type="primary"):
            with st.spinner("Running pipeline..."):
                result = run_pipeline()
            load_table.clear()

            if result.get("status") == "success":
                st.success(
                    f"Pipeline completed successfully. Run ID: {result.get('run_id')}"
                )
            else:
                st.error(
                    "Pipeline failed. "
                    f"Error: {result.get('error_message') or 'Unknown error'}"
                )

    with col2:
        if st.button("Refresh Dashboard"):
            load_table.clear()
            st.info("Dashboard data refreshed.")


def render_latest_run() -> None:
    runs_df = load_table("pipeline_runs")
    st.subheader("Latest Pipeline Run")

    if runs_df.empty:
        st.warning("No pipeline run metadata found yet.")
        return

    runs_df = runs_df.sort_values("run_started_at", ascending=False)
    latest = runs_df.iloc[0]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Status", str(latest["status"]))
    kpi2.metric("Source Rows", int(latest["source_rows"]))
    kpi3.metric("Curated Rows", int(latest["curated_rows"]))
    kpi4.metric("Aggregated Rows", int(latest["aggregated_rows"]))

    st.caption(
        "Started: "
        f"{latest['run_started_at']} | Ended: {latest['run_ended_at']} | "
        f"Duration: {latest['duration_seconds']} seconds"
    )


def render_business_kpis() -> None:
    agg_df = load_table("agg_daily_hospital_kpi")
    st.subheader("Business KPIs")

    if agg_df.empty:
        st.warning("No aggregated KPI table found yet.")
        return

    agg_df["visit_date"] = pd.to_datetime(
        agg_df["visit_date"], errors="coerce")
    agg_df = agg_df.dropna(subset=["visit_date"])

    departments = ["All"] + \
        sorted(agg_df["department"].dropna().unique().tolist())
    admission_types = ["All"] + sorted(
        agg_df["admission_type"].dropna().unique().tolist()
    )
    min_date = agg_df["visit_date"].min().date()
    max_date = agg_df["visit_date"].max().date()

    c1, c2, c3 = st.columns(3)
    selected_department = c1.selectbox("Department", departments)
    selected_admission_type = c2.selectbox("Admission Type", admission_types)
    selected_date_range = c3.date_input(
        "Visit Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    filtered = agg_df.copy()
    if selected_department != "All":
        filtered = filtered[filtered["department"] == selected_department]
    if selected_admission_type != "All":
        filtered = filtered[filtered["admission_type"]
                            == selected_admission_type]

    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        filtered = filtered[
            (filtered["visit_date"].dt.date >= start_date)
            & (filtered["visit_date"].dt.date <= end_date)
        ]

    total_visits = int(filtered["total_visits"].sum())
    total_treatments = int(filtered["total_treatments"].sum())
    total_billing = float(filtered["total_bill_amount"].sum())
    avg_stay = float(filtered["avg_stay_hours"].mean()
                     ) if not filtered.empty else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Visits", f"{total_visits:,}")
    m2.metric("Total Treatments", f"{total_treatments:,}")
    m3.metric("Total Billing", f"{total_billing:,.2f}")
    m4.metric("Avg Stay (hrs)", f"{avg_stay:.2f}")

    trend = (
        filtered.groupby("visit_date", as_index=False)["total_visits"]
        .sum()
        .sort_values("visit_date")
    )
    st.line_chart(trend.set_index("visit_date")["total_visits"], height=250)

    billing_by_department = (
        filtered.groupby("department", as_index=False)["total_bill_amount"]
        .sum()
        .sort_values("total_bill_amount", ascending=False)
    )
    if not billing_by_department.empty:
        st.bar_chart(
            billing_by_department.set_index("department")["total_bill_amount"],
            height=260,
        )

    filtered_for_display = filtered.sort_values(
        ["visit_date", "department", "admission_type"]
    )

    st.dataframe(
        filtered_for_display,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = filtered_for_display.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered KPI CSV",
        data=csv_data,
        file_name="filtered_hospital_kpi.csv",
        mime="text/csv",
    )


def render_reports() -> None:
    st.subheader("Generated Reports")

    col1, col2 = st.columns([1, 1])
    with col1:
        image_path = OUTPUT_DIR / "daily_patient_volume.png"
        if image_path.exists():
            st.image(str(image_path), caption="Daily Patient Volume")
        else:
            st.info("Chart image not found yet.")

    with col2:
        st.markdown(load_report_markdown())


def main() -> None:
    render_header()
    render_controls()
    render_latest_run()
    render_business_kpis()
    render_reports()


if __name__ == "__main__":
    main()
