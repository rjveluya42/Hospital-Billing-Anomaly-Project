"""Interactive dashboard. Start with: python -m streamlit run dashboard.py"""
from pathlib import Path
import pandas as pd
import streamlit as st

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
st.set_page_config(page_title="Hospital Billing Review", layout="wide")
st.title("Hospital Billing Anomaly Detection")
st.caption("Portfolio demonstration using synthetic Kaggle data. Flags are not proof of fraud or billing errors.")

file = RESULTS / "all_records_with_flags.csv"
if not file.exists():
    st.error("Run `python analysis.py` in the project folder first.")
    st.stop()

@st.cache_data
def load_data():
    return pd.read_csv(file)

df = load_data()
conditions = sorted(df["Medical Condition"].dropna().unique())
insurers = sorted(df["Insurance Provider"].dropna().unique())
condition = st.sidebar.multiselect("Medical condition", conditions, default=conditions)
insurer = st.sidebar.multiselect("Insurance provider", insurers, default=insurers)
only_flagged = st.sidebar.checkbox("Show flagged records only", value=False)
filtered = df[df["Medical Condition"].isin(condition) & df["Insurance Provider"].isin(insurer)]
if only_flagged:
    filtered = filtered[filtered["needs_review"]]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Records shown", f"{len(filtered):,}")
c2.metric("Flagged records", f"{int(filtered['needs_review'].sum()):,}")
c3.metric("Negative charges", f"{int(filtered['negative_charge'].sum()):,}")
c4.metric("Exact duplicates", f"{int(filtered['duplicate_row'].sum()):,}")

st.subheader("Billing Review Charts")
left, right = st.columns(2)
with left:
    st.write("Flag counts (current filters)")
    st.bar_chart(pd.Series({"Negative": int(filtered["negative_charge"].sum()), "Duplicate": int(filtered["duplicate_row"].sum()), "High charge": int(filtered["high_charge"].sum())}))
    st.write("Flagged rate by condition (%)")
    rates = filtered.groupby("Medical Condition")["needs_review"].mean().mul(100)
    st.bar_chart(rates)
with right:
    st.write("Flagged rate by insurance provider (%)")
    rates = filtered.groupby("Insurance Provider")["needs_review"].mean().mul(100)
    st.bar_chart(rates)
    st.write("Average nonnegative charges by condition ($)")
    positive = filtered[filtered["Billing Amount"] >= 0]
    st.bar_chart(positive.groupby("Medical Condition")["Billing Amount"].mean())

st.subheader("Monthly review rate")
monthly = filtered.copy()
monthly["month"] = pd.to_datetime(monthly["Date of Admission"], errors="coerce").dt.to_period("M").astype(str)
monthly = monthly[monthly["month"] != "NaT"].groupby("month")["needs_review"].mean().mul(100)
st.line_chart(monthly)
st.caption("Monthly patterns may reflect incomplete months or synthetic data generation.")

st.subheader("Record Review Table")
cols = ["Name", "Medical Condition", "Insurance Provider", "Billing Amount", "Date of Admission", "review_reason"]
st.dataframe(filtered[cols], use_container_width=True, hide_index=True)
st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"), "billing_review.csv", "text/csv")
st.info("Negative amounts can be adjustments or credits. Exact duplicates may be legitimate repeated encounters. No claim of fraud is made.")
