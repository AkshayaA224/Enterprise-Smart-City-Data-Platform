from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "raw" / "traffic.csv"
OUT = ROOT / "reports" / "eda"

df = pd.read_csv(DATA, low_memory=False)

hour_cols = [
    c for c in df.columns
    if c.strip().lower() not in {
        "id", "segmentid", "roadway name", "from", "to", "direction", "date"
    }
]

hours = df[hour_cols].apply(
    lambda s: pd.to_numeric(
        s.astype(str).str.replace(",", "", regex=False).str.strip(),
        errors="coerce"
    )
)

# Find the highest reading in each source hourly column
rows = []

for col in hour_cols:
    idx = hours[col].idxmax()
    if pd.notna(idx):
        rows.append({
            "hour_column": col,
            "maximum_value": hours.loc[idx, col],
            "ID": df.loc[idx, "ID"],
            "SegmentID": df.loc[idx, "SegmentID"],
            "Roadway Name": df.loc[idx, "Roadway Name"],
            "Direction": df.loc[idx, "Direction"],
            "Date": df.loc[idx, "Date"]
        })

result = pd.DataFrame(rows)
result.to_csv(OUT / "traffic_extreme_values.csv", index=False)

print("Highest readings by hourly column:")
print(result.sort_values("maximum_value", ascending=False)
            .head(10).to_string(index=False))
print("\nSaved:", OUT / "traffic_extreme_values.csv")
