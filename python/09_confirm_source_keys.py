import csv
from collections import Counter
from pathlib import Path

BASE = Path("data/raw")

def inspect_csv(filename, key_options):
    with (BASE / filename).open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.DictReader(f)
        total = 0
        counts = {tuple(keys): Counter() for keys in key_options}
        full_rows = Counter()

        for row in reader:
            total += 1
            normalized = {
                k: (v.strip() if v is not None else "")
                for k, v in row.items()
            }
            full_rows[tuple(normalized.values())] += 1

            for keys in key_options:
                key = tuple(normalized.get(k, "") for k in keys)
                if all(key):
                    counts[tuple(keys)][key] += 1

    print(f"\n{filename}: total rows={total}")
    for keys, values in counts.items():
        duplicates = sum(1 for n in values.values() if n > 1)
        duplicate_rows = sum(n - 1 for n in values.values() if n > 1)
        print(
            f"Key {keys}: complete={sum(values.values())}, "
            f"unique={len(values)}, duplicate_groups={duplicates}, "
            f"extra_duplicate_rows={duplicate_rows}"
        )

    exact_duplicate_groups = sum(1 for n in full_rows.values() if n > 1)
    exact_duplicate_extra_rows = sum(n - 1 for n in full_rows.values() if n > 1)
    print("Exact full-row duplicate groups:", exact_duplicate_groups)
    print("Exact full-row extra duplicate rows:", exact_duplicate_extra_rows)

inspect_csv(
    "electricity.csv",
    [
        ["Entity", "Code", "Year"],
        ["Entity", "Year"],
    ],
)

inspect_csv(
    "traffic.csv",
    [
        ["ID"],
        ["ID", "Date"],
        ["SegmentID", "Date"],
    ],
)

inspect_csv(
    "property_tax.csv",
    [
        ["PARID", "YEAR"],
        ["PARID", "YEAR", "RECTYPE", "IDENT", "SUBIDENT"],
    ],
)
