
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "raw" / "electricity.csv"
OUT = ROOT / "reports" / "eda"
CHARTS = OUT / "charts"

OUT.mkdir(parents=True, exist_ok=True)
CHARTS.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SOURCE)

entity_col = "Entity"
year_col = "Year"
demand_col = "Electricity demand"
code_col = "Code"

# Basic validation
df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
df[demand_col] = pd.to_numeric(df[demand_col], errors="coerce")

summary = [
    "ELECTRICITY DATA EDA SUMMARY",
    "=" * 35,
    f"Rows: {len(df)}",
    f"Columns: {len(df.columns)}",
    f"Unique entities: {df[entity_col].nunique()}",
    f"Year range: {df[year_col].min():.0f} to {df[year_col].max():.0f}",
    f"Unique years: {df[year_col].nunique()}",
    f"Exact duplicate rows: {df.duplicated().sum()}",
    f"Duplicate Entity-Year pairs: "
    f"{df.duplicated([entity_col, year_col]).sum()}",
    f"Missing Entity values: {df[entity_col].isna().sum()}",
    f"Missing Code values: {df[code_col].isna().sum()}",
    f"Missing Year values: {df[year_col].isna().sum()}",
    f"Missing demand values: {df[demand_col].isna().sum()}",
    f"Negative demand values: {(df[demand_col] < 0).sum()}",
    f"Zero demand records: {(df[demand_col] == 0).sum()}",
    "",
    "Demand statistics:",
    df[demand_col].describe().to_string(),
]

(OUT / "electricity_eda_summary.txt").write_text(
    "\n".join(summary), encoding="utf-8"
)

# Missing values
df.isna().sum().rename("missing_count").to_csv(
    OUT / "electricity_missing_values.csv"
)

# Entity coverage
coverage = df.groupby(entity_col).agg(
    record_count=(year_col, "count"),
    first_year=(year_col, "min"),
    last_year=(year_col, "max"),
    unique_years=(year_col, "nunique"),
).reset_index()

coverage["missing_years_within_global_range"] = (
    df[year_col].nunique() - coverage["unique_years"]
)

coverage.to_csv(OUT / "electricity_entity_year_coverage.csv", index=False)

# Zero and extreme demand records
df.loc[df[demand_col] == 0].to_csv(
    OUT / "electricity_zero_demand_records.csv", index=False
)

df.nlargest(20, demand_col).to_csv(
    OUT / "electricity_top_20_demand_records.csv", index=False
)

# Annual World trend, if World is present
world = df[df[entity_col].astype(str).str.strip().eq("World")].copy()
world = world.dropna(subset=[year_col, demand_col])
world = world.sort_values(year_col)

if not world.empty:
    plt.figure(figsize=(10, 5))
    plt.plot(world[year_col], world[demand_col], marker="o")
    plt.title("World Electricity Demand by Year")
    plt.xlabel("Year")
    plt.ylabel("Electricity demand (source units)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(CHARTS / "electricity_world_annual_trend.png", dpi=150)
    plt.close()

# Demand distribution: all entities
valid_demand = df[demand_col].dropna()

plt.figure(figsize=(9, 5))
plt.hist(valid_demand, bins=50)
plt.title("Electricity Demand Distribution — All Entities")
plt.xlabel("Electricity demand (source units)")
plt.ylabel("Record count")
plt.tight_layout()
plt.savefig(CHARTS / "electricity_demand_distribution.png", dpi=150)
plt.close()


# Demand distribution using logarithmically spaced bins
positive_demand = valid_demand[valid_demand > 0]

if not positive_demand.empty:
    bins = __import__("numpy").logspace(
        __import__("numpy").log10(positive_demand.min()),
        __import__("numpy").log10(positive_demand.max()),
        50,
    )

    plt.figure(figsize=(9, 5))
    plt.hist(positive_demand, bins=bins)
    plt.xscale("log")
    plt.title("Positive Electricity Demand Distribution")
    plt.xlabel("Electricity demand (log scale; source units)")
    plt.ylabel("Record count")
    plt.tight_layout()
    plt.savefig(
        CHARTS / "electricity_demand_distribution_log.png",
        dpi=150,
    )
    plt.close()
