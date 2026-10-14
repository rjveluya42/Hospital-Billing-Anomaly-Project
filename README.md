# Hospital Billing Anomaly Detection — Python Portfolio Project

A beginner-friendly healthcare analytics project built with **Python, pandas, matplotlib, SQLite, and Streamlit**. Uses a **synthetic** Kaggle dataset, not actual patient billing records.

## Project question
Which records should a billing analyst review because of negative charges, repeated records, or unusually high charges?

## Folder contents
- `analysis.py` — reads the dataset, checks billing data, exports tables, creates five PNG charts and a SQLite database
- `dashboard.py` — interactive browser dashboard with filters, charts, and CSV download
- `Healthcare_Kaggle_Dataset.csv` — original dataset (a ZIP archive with a `.csv` name; script handles this)
- `queries.sql` — example SQL queries
- `results/charts/` — five ready-to-view charts
- `results/` — audit CSVs, summary, monthly results, SQLite database
- `requirements.txt` — Python packages

## Mac instructions (copy one line at a time)
1. Download the ZIP and **double-click to extract it**.
2. Open Terminal and type `cd ` (include the space). Drag the extracted `Hospital_Billing_Simple_Project` folder from Finder into Terminal and press Enter. This avoids incorrect file paths.
3. Install packages: `python -m pip install -r requirements.txt`
4. Regenerate results: `python analysis.py`
5. Open dashboard: `python -m streamlit run dashboard.py`
6. Open the local URL Streamlit prints, usually `http://localhost:8501`.

**VS Code:** Open the extracted project folder, then use Terminal > New Terminal and run steps 3–5. Do not use the regular Python Run button for `dashboard.py`.

**Windows:** Use `py -m pip install -r requirements.txt`, `py analysis.py`, and `py -m streamlit run dashboard.py` if `python` is not recognized.

## How flags work
- **Negative charge:** billing amount below zero (may be a credit or adjustment).
- **Exact duplicate:** row repeats all original fields, excluding the first occurrence. This does **not** prove duplicate billing.
- **High charge:** above Q3 + 1.5 × IQR among nonnegative charges in the same medical condition.
- **Needs review:** at least one of these flags. Flags overlap; do not add category totals to calculate unique records.

This simple version deliberately **does not use machine learning**. It prioritizes readable, reproducible code and transparent rules. It cannot determine fraud, actual revenue, or financial loss. No real hospital conclusions should be drawn from synthetic data.
