
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import hashlib
import json

path = Path("data/raw/emergency.xml")
fingerprints = Counter()
total = 0

for _, element in ET.iterparse(path, events=("end",)):
    if element.tag == "row":
        row = {
            child.tag: (child.text or "").strip()
            for child in element
        }

        fingerprint = hashlib.sha256(
            json.dumps(
                row, sort_keys=True, ensure_ascii=False
            ).encode("utf-8")
        ).hexdigest()

        fingerprints[fingerprint] += 1
        total += 1
        element.clear()

duplicate_groups = sum(
    count > 1 for count in fingerprints.values()
)
extra_rows = sum(
    count - 1 for count in fingerprints.values()
    if count > 1
)

print("Total records:", total)
print("Distinct full-record fingerprints:", len(fingerprints))
print("Exact duplicate groups:", duplicate_groups)
print("Extra exact duplicate rows:", extra_rows)
