import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path

RAW = Path("data/raw")
OUTPUT = Path("reports/data_profiling/data_dictionary.csv")

def infer_type(values):
    values = [v.strip() for v in values if v is not None and str(v).strip()]
    if not values:
        return "unknown"
    try:
        for v in values:
            int(v)
        return "integer"
    except ValueError:
        pass
    try:
        for v in values:
            float(v)
        return "numeric"
    except ValueError:
        return "string"

def csv_columns(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        samples = {h: [] for h in headers}
        for i, row in enumerate(reader):
            for h in headers:
                samples[h].append(row.get(h, ""))
            if i >= 199:
                break
    return [(h, infer_type(samples[h])) for h in headers]

def json_columns(path):
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, dict):
        records = data.get("data", data.get("records", [data]))
    else:
        records = data
    if not isinstance(records, list) or not records:
        return []
    headers = list(records[0].keys()) if isinstance(records[0], dict) else []
    return [(h, infer_type([r.get(h) for r in records[:200] if isinstance(r, dict)]))
            for h in headers]

def xml_columns(path):
    root = ET.parse(path).getroot()
    rows = root.find(".//rows")
    if rows is None or len(rows) == 0:
        return []
    headers = [c.tag for c in rows[0]]
    return [(h, infer_type([r.findtext(h, default="") for r in list(rows)[:200]]))
            for h in headers]

output_rows = []
for path in sorted(RAW.iterdir()):
    if not path.is_file():
        continue
    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            columns = csv_columns(path)
        elif suffix == ".json":
            columns = json_columns(path)
        elif suffix == ".xml":
            columns = xml_columns(path)
        else:
            continue

        for name, dtype in columns:
            output_rows.append({
                "dataset_name": path.stem,
                "source_column": name,
                "source_data_type": dtype,
                "description": "",
                "target_column": "",
                "target_data_type": "",
                "transformation_rule": "",
                "nullable": "To assess"
            })
        print(f"{path.name}: {len(columns)} columns processed")
    except Exception as e:
        print(f"ERROR processing {path.name}: {e}")

fields = [
    "dataset_name", "source_column", "source_data_type", "description",
    "target_column", "target_data_type", "transformation_rule", "nullable"
]
with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(output_rows)

print(f"\nCreated {OUTPUT} with {len(output_rows)} column definitions.")
