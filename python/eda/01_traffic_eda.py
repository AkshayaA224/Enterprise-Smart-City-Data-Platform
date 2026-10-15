from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "traffic.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "eda"
CHART_DIR = OUTPUT_DIR / "charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("TRAFFIC DATA - EXPLORATORY DATA ANALYSIS")
print("=" * 60)

# 1. Load data
df = pd.read_csv(DATA_FILE, low_memory=False)
print("\n1. DATASET OVERVIEW")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
print("\nColumn names:")
print(df.columns.tolist())

# 2. Data types and memory
with open(OUTPUT_DIR / "traffic_eda_summary.txt", "w", encoding="utf-8") as report:
    report.write("TRAFFIC DATA - EXPLORATORY DATA ANALYSIS\n")
    report.write("=" * 60 + "\n\n")

    report.write("1. DATASET OVERVIEW\n")
    report.write(f"Rows: {df.shape[0]}\n")
    report.write(f"Columns: {df.shape[1]}\n\n")

    report.write("2. DATA TYPES\n")
    report.write(df.dtypes.to_string() + "\n\n")

    report.write("3. DESCRIPTIVE STATISTICS\n")
    report.write(df.describe(include="all").transpose().to_string() + "\n\n")

    report.write("4. MISSING VALUES\n")
    missing = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_percent": (df.isna().mean() * 100).round(2)
    }).sort_values("missing_count", ascending=False)
    report.write(missing.to_string() + "\n\n")
    missing.to_csv(OUTPUT_DIR / "traffic_missing_values.csv")

    report.write("5. DUPLICATE ROWS\n")
    report.write(f"Exact duplicate rows: {df.duplicated().sum()}\n\n")

    # 3. Date coverage, if a Date column exists
    date_column = next(
        (col for col in df.columns if col.strip().lower() == "date"),
        None
    )

    if date_column:
        dates = pd.to_datetime(df[date_column], errors="coerce")
        report.write("6. DATE COVERAGE\n")
        report.write(f"Unparseable dates: {dates.isna().sum()}\n")
        if dates.notna().any():
            report.write(f"Earliest date: {dates.min()}\n")
            report.write(f"Latest date: {dates.max()}\n")
            report.write(f"Unique valid dates: {dates.nunique()}\n\n")

            date_counts = dates.dropna().dt.to_period("M").value_counts().sort_index()
            plt.figure(figsize=(12, 5))
            date_counts.plot(kind="bar")
            plt.title("Traffic Records by Month")
            plt.xlabel("Month")
            plt.ylabel("Number of Records")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(CHART_DIR / "traffic_records_by_month.png", dpi=150)
            plt.close()

    # 4. Identify hourly traffic columns without assuming their values are valid
    id_columns = {
        "id", "segmentid", "roadway name", "from", "to",
        "direction", "date"
    }
    hourly_columns = [
        col for col in df.columns
        if col.strip().lower() not in id_columns
    ]

    numeric_hours = df[hourly_columns].apply(
        lambda column: pd.to_numeric(
            column.astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce"
        )
    )

    # Save descriptive statistics for hourly columns
    report.write("7. HOURLY TRAFFIC VALUE SUMMARY\n")
    report.write(numeric_hours.describe().transpose().to_string() + "\n\n")

    report.write("8. HOURLY COLUMN VALIDATION\n")
    report.write(
        "Hourly columns are identified by excluding known identifier columns. "
        "Their labels and mappings must be checked because source labels may "
        "have inconsistent spacing or formatting.\n\n"
    )
    report.write("Hourly columns detected:\n")
    report.write("\n".join(hourly_columns) + "\n")

    # 5. Missing values in hourly columns
    hourly_missing = numeric_hours.isna().sum().sort_values(ascending=False)
    hourly_missing.to_csv(OUTPUT_DIR / "traffic_hourly_missing_values.csv",
                          header=["unparseable_or_missing_count"])

    # 6. Plot distributions of hourly values
    all_hourly_values = numeric_hours.stack().dropna()

    if not all_hourly_values.empty:
        plt.figure(figsize=(10, 5))
        plt.hist(all_hourly_values, bins=40, edgecolor="black")
        plt.title("Distribution of Hourly Traffic Values")
        plt.xlabel("Traffic Value")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(CHART_DIR / "hourly_traffic_distribution.png", dpi=150)
        plt.close()

        plt.figure(figsize=(12, 5))
        numeric_hours.boxplot(rot=90)
        plt.title("Hourly Traffic Values - Boxplot")
        plt.xlabel("Source Hourly Column")
        plt.ylabel("Traffic Value")
        plt.tight_layout()
        plt.savefig(CHART_DIR / "hourly_traffic_boxplot.png", dpi=150)
        plt.close()

    # 7. Mean values by source column (not a verified chronological profile)
    mean_by_column = numeric_hours.mean()
    mean_by_column.to_csv(
        OUTPUT_DIR / "traffic_hourly_column_means.csv",
        header=["mean_traffic_value"]
    )

print("\nEDA completed.")
print("Text report:", OUTPUT_DIR / "traffic_eda_summary.txt")
print("Charts:", CHART_DIR)
print("Note: hourly column ordering and mappings need separate validation.")
