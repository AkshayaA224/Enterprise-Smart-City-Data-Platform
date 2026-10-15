from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / "data" / "raw" / "traffic.csv", low_memory=False)
OUT = ROOT / "reports" / "eda"

segment = df[
    df["SegmentID"].eq(139303)
    & df["Roadway Name"].eq("BRONX RIVER PARKWAY")
].copy()

hour_cols = [
    c for c in df.columns
    if c.strip().lower() not in {
        "id", "segmentid", "roadway name", "from", "to", "direction", "date"
    }
]

for col in hour_cols:
    segment[col] = pd.to_numeric(
        segment[col].astype(str).str.replace(",", "", regex=False).str.strip(),
        errors="coerce"
    )

segment["row_max_traffic_value"] = segment[hour_cols].max(axis=1)
segment["row_mean_traffic_value"] = segment[hour_cols].mean(axis=1)

segment.to_csv(OUT / "bronx_river_parkway_segment_analysis.csv", index=False)

print("Matching records:", len(segment))
print("Dates covered:", segment["Date"].nunique())
print("\nHighest 10 records for this segment:")
print(
    segment.sort_values("row_max_traffic_value", ascending=False)[
        ["ID", "SegmentID", "Roadway Name", "Direction", "Date",
         "row_max_traffic_value", "row_mean_traffic_value"]
    ].head(10).to_string(index=False)
)
print("\nSaved segment analysis report.")
