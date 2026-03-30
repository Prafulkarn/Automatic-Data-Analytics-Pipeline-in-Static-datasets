import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# Connect to your existing database
conn = sqlite3.connect("data/hospital_analytics.db")

st.title("🏥 Hospital Analytics Dashboard")

# ── Sidebar Filters ──
departments = pd.read_sql("SELECT DISTINCT department FROM agg_daily_hospital_kpi", conn)
selected_dept = st.sidebar.multiselect("Department", departments["department"].tolist(), default=departments["department"].tolist())

date_range = st.sidebar.date_input("Date Range", [])

# ── KPI Cards at the top ──
kpi_df = pd.read_sql("SELECT * FROM agg_daily_hospital_kpi", conn)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Visits",     f"{kpi_df['total_visits'].sum():,}")
col2.metric("Total Treatments", f"{kpi_df['total_treatments'].sum():,}")
col3.metric("Total Billing",    f"₹{kpi_df['total_bill_amount'].sum():,.0f}")
col4.metric("Avg Stay (hrs)",   f"{kpi_df['avg_stay_hours'].mean():.1f}")

# ── Interactive Chart ──
daily = kpi_df[kpi_df["department"].isin(selected_dept)]
daily = daily.groupby("visit_date")["total_visits"].sum().reset_index()

fig = px.line(daily, x="visit_date", y="total_visits",
              title="Daily Patient Visits",
              markers=True)
st.plotly_chart(fig, use_container_width=True)

# ── Department Breakdown ──
dept_fig = px.bar(
    kpi_df.groupby("department")["total_visits"].sum().reset_index(),
    x="department", y="total_visits",
    title="Visits by Department", color="department"
)
st.plotly_chart(dept_fig, use_container_width=True)

# ── Raw Data Table ──
if st.checkbox("Show raw data"):
    st.dataframe(kpi_df)