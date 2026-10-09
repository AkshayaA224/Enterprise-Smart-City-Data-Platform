
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json

path = Path("data/raw/emergency.xml")
counts = Counter()
examples = defaultdict(list)
total = 0

for _, element in ET.iterparse(path, events=("end",)):
    if element.tag == "row":
        row = {
            child.tag: (child.text or "").strip()
            for child in element
        }

        total += 1
        key = tuple(
            row.get(field, "")
            for field in [
                "incident_type",
                "location",
                "borough",
                "creation_date",
                "latitude",
                "longitude",
            ]
        )

        if all(key):
            fingerprint = hashlib.sha256(
                json.dumps(
                    row, sort_keys=True, ensure_ascii=False
                ).encode("utf-8")
            ).hexdigest()
            counts[key] += 1

            if len(examples[key]) < 3:
                examples[key].append((fingerprint, row))

        element.clear()

duplicate_keys = [
    (key, rows)
    for key, rows in examples.items()
    if counts[key] > 1
]

print("Total XML records:", total)
print("Complete-key groups with duplicates:",
      sum(1 for key, count in counts.items() if count > 1))
print("Extra rows across complete-key duplicates:",
      sum(count - 1 for count in counts.values() if count > 1))

for key, rows in duplicate_keys[:5]:
    print("\nRepeated key:", key)
    print("Total records for key:", counts[key])
    for fingerprint, row in rows:
        print("Fingerprint:", fingerprint)
        print("Record:", row)
