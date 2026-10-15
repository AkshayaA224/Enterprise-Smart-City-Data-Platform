from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "raw" / "traffic.csv"
OUT = ROOT / "reports" / "eda"

df = pd.read_csv(DATA, low_memory=False)

id_cols = {
    "id", "segmentid", "roadway name", "from", "to", "direction", "date"
}
hour_cols = [c for c in df.columns if c.strip().lower() not in id_cols]

hours = df[hour_cols].apply(
    lambda s: pd.to_numeric(
        s.astype(str).str.replace(",", "", regex=False).str.strip(),
        errors="coerce"
    )
)

results = []

for col in hour_cols:
    s = hours[col].dropna()
    if s.empty:
        continue

    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    results.append({
        "hour_column": col,
        "valid_values": len(s),
        "zero_count": int((s == 0).sum()),
        "zero_percent": round((s == 0).mean() * 100, 2),
        "negative_count": int((s < 0).sum()),
        "mean": round(s.mean(), 2),
        "median": round(s.median(), 2),
        "maximum": round(s.max(), 2),
        "iqr_outlier_count": int(((s < lower) | (s > upper)).sum()),
        "iqr_upper_limit": round(upper, 2)
    })

result = pd.DataFrame(results)
result.to_csv(OUT / "traffic_outlier_zero_analysis.csv", index=False)

print("Traffic quality checks completed.")
print("\nColumns with the most IQR outliers:")
print(
    result.sort_values("iqr_outlier_count", ascending=False)
          .head(5).to_string(index=False)
)
print("\nColumns with the most zero values:")
print(
    result.sort_values("zero_count", ascending=False)
          .head(5).to_string(index=False)
)
print("\nSaved:", OUT / "traffic_outlier_zero_analysis.csv")
