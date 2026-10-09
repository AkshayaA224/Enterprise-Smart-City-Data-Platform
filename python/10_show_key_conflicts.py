import csv
from collections import defaultdict
from pathlib import Path

BASE = Path("data/raw")


def show_conflicts(filename, key_fields, display_fields, limit=3):
    groups = defaultdict(list)

    with (BASE / filename).open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        for row in csv.DictReader(f):
            normalized = {
                key: (value.strip() if value else "")
                for key, value in row.items()
            }
            key = tuple(normalized.get(field, "") for field in key_fields)

            if all(key):
                groups[key].append(normalized)

    conflicts = [
        (key, rows)
        for key, rows in groups.items()
        if len(rows) > 1
    ]

    print(f"\n{filename}: key={key_fields}")
    print("Duplicate key groups:", len(conflicts))

    for key, rows in conflicts[:limit]:
        print("\nKey:", key)
        for row in rows[:3]:
            print({
                field: row.get(field, "")
                for field in display_fields
            })


show_conflicts(
    "traffic.csv",
    ["ID"],
    ["ID", "SegmentID", "Roadway Name", "Date", "Direction"],
)

show_conflicts(
    "traffic.csv",
    ["ID", "Date"],
    ["ID", "SegmentID", "Roadway Name", "Date", "Direction"],
)

show_conflicts(
    "traffic.csv",
    ["SegmentID", "Date"],
    ["ID", "SegmentID", "Roadway Name", "Date", "Direction"],
)

show_conflicts(
    "property_tax.csv",
    ["PARID", "YEAR"],
    ["PARID", "YEAR", "BORO", "BLOCK", "LOT", "RECTYPE",
     "IDENT", "SUBIDENT", "AVTOT", "AVLAND", "AVTOT2"],
)
