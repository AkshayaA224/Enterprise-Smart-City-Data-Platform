
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "raw" / "parking.json"
OUT = ROOT / "reports" / "eda"
CHARTS = OUT / "charts"

OUT.mkdir(parents=True, exist_ok=True)
CHARTS.mkdir(parents=True, exist_ok=True)

df = pd.read_json(SOURCE)

numeric_cols = [
    "Occupancy_Rate",
    "Payment_Amount",
    "Parking_Duration",
    "Dynamic_Pricing_Factor",
    "Weather_Temperature",
    "Weather_Precipitation",
    "Sensor_Reading_Proximity",
    "Sensor_Reading_Pressure",
    "Vehicle_Type_Weight",
    "Vehicle_Type_Height",
    "Sensor_Reading_Ultrasonic",
    "Environmental_Noise_Level",
    "Proximity_To_Exit",
    "User_Parking_History",
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

summary = [
    "PARKING DATA EDA SUMMARY",
    "=" * 35,
    f"Rows: {len(df)}",
    f"Columns: {len(df.columns)}",
    f"Unique parking spots: {df['Parking_Spot_ID'].nunique()}",
    f"Exact duplicate rows: {df.duplicated().sum()}",
    f"Duplicate timestamps: {df['Timestamp'].duplicated().sum()}",
    f"Missing values: {df.isna().sum().sum()}",
    f"Zero-duration records: {(df['Parking_Duration'] == 0).sum()}",
    f"Negative-duration records: {(df['Parking_Duration'] < 0).sum()}",
    (
        "Occupancy rates outside 0-1: "
        f"{((df['Occupancy_Rate'] < 0) | (df['Occupancy_Rate'] > 1)).sum()}"
    ),
    f"Negative payment amounts: {(df['Payment_Amount'] < 0).sum()}",
    f"Non-positive durations: {(df['Parking_Duration'] <= 0).sum()}",
    "",
    "Numeric summary:",
    df[numeric_cols].describe().to_string(),
    "",
    "Categorical counts:",
]

categorical_cols = [
    "User_Type",
    "Nearby_Traffic_Level",
    "Parking_Lot_Section",
    "Payment_Status",
    "Occupancy_Status",
    "Vehicle_Type",
    "Spot_Size",
]

for col in categorical_cols:
    summary.extend([
        "",
        f"{col}:",
        df[col].value_counts(dropna=False).to_string(),
    ])

(OUT / "parking_eda_summary.txt").write_text(
    "\n".join(summary), encoding="utf-8"
)

df.isna().sum().rename("missing_count").to_csv(
    OUT / "parking_missing_values.csv"
)

df.loc[df["Parking_Duration"] <= 0].to_csv(
    OUT / "parking_nonpositive_duration_records.csv",
    index=False,
)

for col in categorical_cols:
    df[col].value_counts(dropna=False).rename("record_count").to_csv(
        OUT / f"parking_{col.lower()}_counts.csv"
    )

# Occupancy status counts
counts = df["Occupancy_Status"].value_counts()
plt.figure(figsize=(7, 5))
counts.plot(kind="bar")
plt.title("Parking Records by Occupancy Status")
plt.xlabel("Occupancy status")
plt.ylabel("Record count")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(CHARTS / "parking_occupancy_status.png", dpi=150)
plt.close()

# Payment status counts
counts = df["Payment_Status"].value_counts()
plt.figure(figsize=(7, 5))
counts.plot(kind="bar")
plt.title("Parking Records by Payment Status")
plt.xlabel("Payment status")
plt.ylabel("Record count")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(CHARTS / "parking_payment_status.png", dpi=150)
plt.close()

# Parking duration distribution, including zero-duration records
plt.figure(figsize=(8, 5))
plt.hist(df["Parking_Duration"].dropna(), bins=range(0, 12))
plt.title("Parking Duration Distribution")
plt.xlabel("Recorded parking duration")
plt.ylabel("Record count")
plt.tight_layout()
plt.savefig(CHARTS / "parking_duration_distribution.png", dpi=150)
plt.close()

# Payment amount distribution
plt.figure(figsize=(8, 5))
plt.hist(df["Payment_Amount"].dropna(), bins=30)
plt.title("Parking Payment Amount Distribution")
plt.xlabel("Payment amount (source units)")
plt.ylabel("Record count")
plt.tight_layout()
plt.savefig(CHARTS / "parking_payment_distribution.png", dpi=150)
plt.close()

print("Parking EDA completed.")
print(f"Summary: {OUT / 'parking_eda_summary.txt'}")
print(f"Charts: {CHARTS}")
