
import csv
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path("data/raw")


def read_csv(filename):
    with (BASE / filename).open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        return [
            {
                k: (v.strip() if v else "")
                for k, v in row.items()
            }
            for row in csv.DictReader(f)
        ]


# 1. Validate the traffic candidate key
traffic = read_csv("traffic.csv")

for fields in [
    ["SegmentID", "Date", "Direction"],
    ["SegmentID", "Date", "Direction", "ID"],
]:
    counts = Counter(
        tuple(row.get(field, "") for field in fields)
        for row in traffic
        if all(row.get(field, "") for field in fields)
    )
    duplicates = sum(n > 1 for n in counts.values())
    extra_rows = sum(n - 1 for n in counts.values() if n > 1)

    print(f"\nTraffic key: {fields}")
    print("Complete unique keys:", len(counts))
    print("Duplicate key groups:", duplicates)
    print("Extra duplicate rows:", extra_rows)


# 2. Inspect property-tax records with repeated PARID + YEAR
property_rows = read_csv("property_tax.csv")
groups = defaultdict(list)

for row in property_rows:
    key = (row.get("PARID", ""), row.get("YEAR", ""))
    if all(key):
        groups[key].append(row)

conflicts = [
    (key, rows)
    for key, rows in groups.items()
    if len(rows) > 1
]

print("\nProperty tax repeated PARID + YEAR groups:", len(conflicts))

for key, rows in conflicts[:5]:
    print("\nKey:", key, "| rows:", len(rows))

    differing = [
        field for field in rows[0]
        if len({row.get(field, "") for row in rows}) > 1
    ]

    print("Differing columns:", differing)

    for row in rows[:3]:
        print({field: row.get(field, "") for field in differing})


# 3. Check whether any property-tax key is complete and unique
for fields in [
    ["PARID", "YEAR"],
    ["PARID", "YEAR", "RECTYPE", "IDENT", "SUBIDENT"],
]:
    keys = [
        tuple(row.get(field, "") for field in fields)
        for row in property_rows
        if all(row.get(field, "") for field in fields)
    ]
    counts = Counter(keys)

    print(f"\nProperty tax key: {fields}")
    print("Complete rows:", len(keys))
    print("Unique keys:", len(counts))
    print("Duplicate groups:", sum(n > 1 for n in counts.values()))
    print("Extra duplicate rows:", sum(n - 1 for n in counts.values()))
