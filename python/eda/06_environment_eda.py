
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "raw" / "environment.csv"
OUT = ROOT / "reports" / "eda"
CHARTS = OUT / "charts"

OUT.mkdir(parents=True, exist_ok=True)
CHARTS.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SOURCE)

value_col = "Data Value"
name_col = "Name"
period_col = "Time Period"
measure_col = "Measure"
unit_col = "Measure Info"

df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

# Summary report
summary = [
    "ENVIRONMENT DATA EDA SUMMARY",
    "=" * 35,
    f"Rows: {len(df)}",
    f"Columns: {len(df.columns)}",
    f"Unique indicators: {df[name_col].nunique()}",
    f"Geographic types: {df['Geo Type Name'].nunique()}",
    f"Exact duplicate rows: {df.duplicated().sum()}",
    f"Duplicate Unique IDs: {df['Unique ID'].duplicated().sum()}",
        (
        "Duplicate analytical combinations: "
        + str(
            df.duplicated(
                [
                    name_col,
                    measure_col,
                    unit_col,
                    "Geo Type Name",
                    "Geo Join ID",
                    period_col,
                ]
            ).sum()
        )
    ),
    "",
    "Missing values by column:",
    df.isna().sum().to_string(),
    "",
    "Indicator counts:",
    df[name_col].value_counts().to_string(),
    "",
    "Geographic type counts:",
    df["Geo Type Name"].value_counts().to_string(),
    "",
    "Data Value summary:",
    df[value_col].describe().to_string(),
    "",
    f"Zero values: {(df[value_col] == 0).sum()}",
    f"Negative values: {(df[value_col] < 0).sum()}",
]

(OUT / "environment_eda_summary.txt").write_text(
    "\n".join(summary), encoding="utf-8"
)

# Quality reports
df.isna().sum().rename("missing_count").to_csv(
    OUT / "environment_missing_values.csv"
)

df[name_col].value_counts().rename("record_count").to_csv(
    OUT / "environment_indicator_counts.csv"
)

df["Geo Type Name"].value_counts().rename("record_count").to_csv(
    OUT / "environment_geographic_type_counts.csv"
)

df.loc[df[value_col] == 0].to_csv(
    OUT / "environment_zero_value_records.csv", index=False
)

# Annual mean trends for pollution indicators.
# Use only annual mean rows with single-year numeric periods.
period_text = df[period_col].astype(str).str.strip()
annual_mask = period_text.str.fullmatch(r"\d{4}")
annual = df.loc[annual_mask].copy()
annual["Year"] = pd.to_numeric(
    annual[period_col], errors="coerce"
)

for indicator, filename, title in [
    (
        "Fine particles (PM 2.5)",
        "environment_pm25_annual_trend.png",
        "PM2.5 Annual Mean by Year",
    ),
    (
        "Nitrogen dioxide (NO2)",
        "environment_no2_annual_trend.png",
        "NO2 Annual Mean by Year",
    ),
]:
    subset = annual[
        (annual[name_col] == indicator)
        & (annual[measure_col] == "Annual mean")
    ].copy()

    if subset.empty:
        print(f"No annual-mean rows found for {indicator}; chart skipped.")
        continue

    # Do not mix different geographic types or units in a single trend.
    # Prefer citywide data when available.
    citywide = subset[subset["Geo Type Name"] == "Citywide"]
    if not citywide.empty:
        subset = citywide

    trend = (
        subset.groupby("Year", as_index=False)[value_col]
        .mean()
        .sort_values("Year")
    )

    plt.figure(figsize=(10, 5))
    plt.plot(trend["Year"], trend[value_col], marker="o")
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel(f"{measure_col}: {subset[unit_col].iloc[0]}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(CHARTS / filename, dpi=150)
    plt.close()

# Distribution by indicator. Different indicators have different units,
# so use separate panels/files for the largest indicators instead of
# combining their values into one histogram.
for indicator, filename in [
    ("Fine particles (PM 2.5)", "environment_pm25_distribution.png"),
    ("Nitrogen dioxide (NO2)", "environment_no2_distribution.png"),
    ("Ozone (O3)", "environment_ozone_distribution.png"),
]:
    subset = df.loc[df[name_col] == indicator, value_col].dropna()

    if subset.empty:
        continue

    plt.figure(figsize=(9, 5))
    plt.hist(subset, bins=40)
    plt.title(f"{indicator} — Value Distribution")
    plt.xlabel(f"Data Value ({df.loc[df[name_col] == indicator, unit_col].mode().iloc[0]})")
    plt.ylabel("Record count")
    plt.tight_layout()
    plt.savefig(CHARTS / filename, dpi=150)
    plt.close()

print("Environment EDA completed.")
print(f"Summary: {OUT / 'environment_eda_summary.txt'}")
print(f"Charts: {CHARTS}")
