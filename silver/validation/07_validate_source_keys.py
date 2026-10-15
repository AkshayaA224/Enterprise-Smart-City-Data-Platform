import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path("data/raw")

KEYS = {
    "citizen_services": ["objectid"],
    "electricity": ["Entity", "Code", "Year"],
    "emergency": [
        "incident_type", "location", "borough",
        "creation_date", "latitude", "longitude"
    ],
    "environment": ["Unique ID"],
    "parking": [],
    "property_tax": ["PARID", "YEAR"],
    "traffic": ["ID"],
    "transport": ["service_date", "day_type"],
    "waste": ["MONTH", "BOROUGH", "COMMUNITYDISTRICT"],
    "water": ["cnty_fips"],
}

FILES = {
    "citizen_services": "citizen_services.csv",
    "electricity": "electricity.csv",
    "emergency": "emergency.xml",
    "environment": "environment.csv",
    "parking": "parking.json",
    "property_tax": "property_tax.csv",
    "traffic": "traffic.csv",
    "transport": "transport.csv",
    "waste": "waste.csv",
    "water": "water.csv",
}

def records(dataset, path):
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            yield from csv.DictReader(f)

    elif path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8-sig") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Expected a JSON array")
        yield from data

    elif path.suffix.lower() == ".xml":
        for _, element in ET.iterparse(path, events=("end",)):
            if element.tag == "row":
                yield {child.tag: child.text for child in element}
                element.clear()

for dataset, filename in FILES.items():
    path = BASE / filename
    key_fields = KEYS[dataset]
    seen = set()
    rows = 0
    missing = 0
    duplicate = 0

    try:
        for row in records(dataset, path):
            rows += 1

            if key_fields:
                values = [row.get(k) for k in key_fields]
                if any(v is None or str(v).strip() == "" for v in values):
                    missing += 1
                    continue
                key = tuple(str(v).strip() for v in values)
            else:
                # Deterministic fallback for sources without a candidate key.
                key = json.dumps(
                    row, sort_keys=True, ensure_ascii=False, default=str
                )

            if key in seen:
                duplicate += 1
            else:
                seen.add(key)

        print(
            f"{dataset}: rows={rows}, key_fields={key_fields or 'FULL_RECORD_HASH'}, "
            f"missing_keys={missing}, duplicate_keys={duplicate}, "
            f"unique_keys={len(seen)}"
        )

    except Exception as exc:
        print(f"{dataset}: ERROR: {exc}")
