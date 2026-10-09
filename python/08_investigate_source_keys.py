import csv
import json
from collections import Counter
from pathlib import Path

BASE = Path("data/raw")

def csv_rows(filename):
    with (BASE / filename).open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        yield from csv.DictReader(f)

# Electricity: inspect missing-key patterns.
missing = Counter()
examples = []

for row in csv_rows("electricity.csv"):
    fields = ["Entity", "Code", "Year"]
    absent = tuple(
        field for field in fields
        if row.get(field) is None or not row[field].strip()
    )
    if absent:
        missing[absent] += 1
        if len(examples) < 5:
            examples.append({k: row.get(k) for k in fields})

print("\nELECTRICITY missing-key patterns:", missing)
print("ELECTRICITY examples:", examples)

# Property tax: inspect duplicate candidate keys and missing keys.
groups = {}
missing_count = 0

for row in csv_rows("property_tax.csv"):
    parid = (row.get("PARID") or "").strip()
    year = (row.get("YEAR") or "").strip()

    if not parid or not year:
        missing_count += 1
        continue

    groups.setdefault((parid, year), []).append(row)

duplicates = [
    (key, rows) for key, rows in groups.items()
    if len(rows) > 1
]

print("\nPROPERTY TAX missing key rows:", missing_count)
print("PROPERTY TAX duplicate key groups:", len(duplicates))
for key, rows in duplicates[:5]:
    print("KEY:", key, "ROWS:", len(rows))
    for row in rows[:2]:
        print({
            k: row.get(k)
            for k in ("PARID", "YEAR", "BORO", "BLOCK", "LOT", "RECTYPE")
        })

# Traffic: inspect whether repeated IDs occur across dates/segments.
id_groups = {}
for row in csv_rows("traffic.csv"):
    key = (row.get("ID") or "").strip()
    if key:
        id_groups.setdefault(key, []).append(row)

repeated = [(key, rows) for key, rows in id_groups.items() if len(rows) > 1]

print("\nTRAFFIC unique IDs:", len(id_groups))
print("TRAFFIC repeated-ID groups:", len(repeated))
for key, rows in repeated[:3]:
    print("ID:", key)
    for row in rows[:3]:
        print({
            k: row.get(k)
            for k in ("ID", "SegmentID", "Roadway Name", "Direction", "Date")
        })

# Emergency: determine whether duplicate proposed keys have identical payloads.
# XML rows were converted to dictionaries in the previous validator; here we
# inspect XML separately with ElementTree for a clear diagnostic.
import xml.etree.ElementTree as ET

counts = Counter()
payloads = {}

for _, element in ET.iterparse(BASE / "emergency.xml", events=("end",)):
    if element.tag == "row":
        row = {child.tag: child.text for child in element}
        key_fields = [
            "incident_type", "location", "borough",
            "creation_date", "latitude", "longitude"
        ]
        absent = tuple(
            field for field in key_fields
            if row.get(field) is None or not str(row[field]).strip()
        )
        if absent:
            counts[absent] += 1
        else:
            key = tuple(str(row[field]).strip() for field in key_fields)
            payloads.setdefault(key, set()).add(
                json.dumps(row, sort_keys=True, ensure_ascii=False)
            )
        element.clear()

print("\nEMERGENCY missing-key patterns:", counts.most_common(10))
duplicate_groups = [
    (key, values) for key, values in payloads.items()
    if len(values) > 1
]
print("EMERGENCY complete-key groups with differing payloads:",
      len(duplicate_groups))
print("EMERGENCY complete-key groups with identical payloads:",
      sum(1 for values in payloads.values() if len(values) == 1))
