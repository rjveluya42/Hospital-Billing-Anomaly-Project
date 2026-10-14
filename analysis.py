"""Simple billing anomaly analysis. Run: python analysis.py"""
from pathlib import Path
import sqlite3
import zipfile
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CHARTS = RESULTS / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)
DATA = HERE / "Healthcare_Kaggle_Dataset.csv"

# Kaggle download may be a ZIP file even though its name ends in .csv.
if zipfile.is_zipfile(DATA):
    with zipfile.ZipFile(DATA) as archive:
        with archive.open("healthcare_dataset.csv") as file:
            df = pd.read_csv(file)
else:
    df = pd.read_csv(DATA)

# Billing rules: negative amounts, exact duplicates, and unusually high charges.
df["negative_charge"] = df["Billing Amount"] < 0
# Compare original fields only; don't count the flags we just added.
original_columns = [c for c in df.columns if c != "negative_charge"]
df["duplicate_row"] = df.duplicated(subset=original_columns, keep="first")
# IQR threshold is calculated within each medical condition, using nonnegative bills.
valid = df.loc[df["Billing Amount"] >= 0]
thresholds = {}
for condition, group in valid.groupby("Medical Condition"):
    q1 = group["Billing Amount"].quantile(0.25)
    q3 = group["Billing Amount"].quantile(0.75)
    thresholds[condition] = q3 + 1.5 * (q3 - q1)
df["high_charge"] = df.apply(
    lambda row: row["Billing Amount"] > thresholds.get(row["Medical Condition"], float("inf")), axis=1
)
df["needs_review"] = df[["negative_charge", "duplicate_row", "high_charge"]].any(axis=1)
df["review_reason"] = df.apply(lambda r: ", ".join([
    name for flag, name in [("negative_charge", "Negative charge"), ("duplicate_row", "Exact duplicate"), ("high_charge", "High charge")]
    if r[flag]
]) or "Not flagged", axis=1)

def save_chart(name):
    plt.tight_layout()
    plt.savefig(CHARTS / name, dpi=170, bbox_inches="tight")
    plt.close()

counts = pd.Series({
    "Negative charges": int(df["negative_charge"].sum()),
    "Exact duplicates": int(df["duplicate_row"].sum()),
    "High charges (IQR)": int(df["high_charge"].sum()),
})
plt.figure(figsize=(9, 5))
bars = plt.bar(counts.index, counts.values)
plt.title("Billing Data Quality Flags")
plt.ylabel("Number of records")
plt.bar_label(bars)
save_chart("01_anomaly_counts.png")

by_condition = df.groupby("Medical Condition")["needs_review"].mean().mul(100).sort_values()
plt.figure(figsize=(9, 5))
plt.barh(by_condition.index, by_condition.values)
plt.xlabel("Flagged records (%)")
plt.title("Billing Review Rate by Medical Condition")
save_chart("02_condition_review_rates.png")

by_insurer = df.groupby("Insurance Provider")["needs_review"].mean().mul(100).sort_values()
plt.figure(figsize=(9, 5))
plt.barh(by_insurer.index, by_insurer.values)
plt.xlabel("Flagged records (%)")
plt.title("Billing Review Rate by Insurance Provider")
save_chart("03_insurer_review_rates.png")

positive = df.loc[df["Billing Amount"] >= 0]
mean_billing = positive.groupby("Medical Condition")["Billing Amount"].mean().sort_values()
plt.figure(figsize=(9, 5))
plt.barh(mean_billing.index, mean_billing.values)
plt.xlabel("Average billed charge ($)")
plt.title("Average Nonnegative Billed Charge by Condition")
save_chart("04_average_charges.png")

df["month"] = pd.to_datetime(df["Date of Admission"], errors="coerce").dt.to_period("M").astype(str)
monthly = df.loc[df["month"] != "NaT"].groupby("month").agg(records=("needs_review", "size"), flagged=("needs_review", "sum"))
monthly["flag_rate_pct"] = monthly["flagged"] / monthly["records"] * 100
monthly.to_csv(RESULTS / "monthly_summary.csv")
plt.figure(figsize=(11, 5))
plt.plot(monthly.index, monthly["flag_rate_pct"])
plt.xticks(range(0, len(monthly), 6), monthly.index[::6], rotation=45)
plt.ylabel("Flagged records (%)")
plt.title("Monthly Billing Review Rate (Synthetic Data)")
save_chart("05_monthly_review_rate.png")

# Keep all records for auditability. No real patient data is used.
df.to_csv(RESULTS / "all_records_with_flags.csv", index=False)
df.loc[df["needs_review"]].to_csv(RESULTS / "flagged_records.csv", index=False)
summary = pd.DataFrame({"metric": ["Original records", "Negative charges", "Additional exact duplicates", "High charges (IQR)", "Unique records flagged"],
                        "count": [len(df), int(df["negative_charge"].sum()), int(df["duplicate_row"].sum()), int(df["high_charge"].sum()), int(df["needs_review"].sum())]})
summary.to_csv(RESULTS / "summary.csv", index=False)
with sqlite3.connect(RESULTS / "billing_analysis.sqlite") as conn:
    df.to_sql("billing_records", conn, if_exists="replace", index=False)
    summary.to_sql("summary", conn, if_exists="replace", index=False)
print("Analysis complete! Open results/charts for 5 PNG charts.")
print(summary.to_string(index=False))
print("To open the interactive dashboard: python -m streamlit run dashboard.py")
