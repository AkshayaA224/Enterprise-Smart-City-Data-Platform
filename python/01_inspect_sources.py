import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path

DATA_DIR = Path("data/raw")

def inspect_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader, [])
        count = sum(1 for row in reader)
    return count, headers

for path in sorted(DATA_DIR.iterdir()):
    if not path.is_file():
        continue

    print(f"\n{'=' * 60}\nFile: {path.name}")

    try:
        if path.suffix.lower() == ".csv":
            count, headers = inspect_csv(path)
            print(f"Data records: {count:,}")
            print(f"Columns ({len(headers)}): {headers}")

        elif path.suffix.lower() == ".json":
            with path.open("r", encoding="utf-8-sig") as f:
                data = json.load(f)

            if isinstance(data, list):
                print(f"Top-level records: {len(data):,}")
                if data and isinstance(data[0], dict):
                    print(f"Fields: {list(data[0].keys())}")
            elif isinstance(data, dict):
                print(f"Top-level keys: {list(data.keys())}")
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"List '{key}': {len(value):,} items")
            else:
                print(f"Top-level JSON type: {type(data).__name__}")

        elif path.suffix.lower() == ".xml":
            root = ET.parse(path).getroot()
            print(f"Root element: {root.tag}")
            print(f"Direct child elements: {len(root)}")
            if len(root):
                print(f"First child element: {root[0].tag}")
                print(f"First child fields: {[child.tag for child in root[0]]}")

        else:
            print("Format not yet supported by this inspection script.")

    except Exception as e:
        print(f"Inspection error: {type(e).__name__}: {e}")
