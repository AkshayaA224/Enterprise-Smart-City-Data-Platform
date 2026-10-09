import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path

base = Path("data/raw")

for path in sorted(base.iterdir()):
    if not path.is_file():
        continue

    print(f"\n{'=' * 60}\n{path.name}")

    try:
        if path.suffix.lower() == ".csv":
            with path.open(
                "r", encoding="utf-8-sig", newline=""
            ) as f:
                reader = csv.reader(f)
                print("HEADERS:", next(reader, []))

        elif path.suffix.lower() == ".json":
            with path.open("r", encoding="utf-8-sig") as f:
                data = json.load(f)

            if isinstance(data, list):
                sample = data[0] if data else {}
            elif isinstance(data, dict):
                sample = next(
                    (
                        data[k][0]
                        for k in ("data", "records", "results")
                        if isinstance(data.get(k), list)
                        and data[k]
                    ),
                    data
                )

            print(
                "ROOT TYPE:", type(data).__name__,
                "\nSAMPLE FIELDS:",
                list(sample.keys())
                if isinstance(sample, dict)
                else type(sample).__name__
            )

        elif path.suffix.lower() == ".xml":
            for _, element in ET.iterparse(path, events=("end",)):
                if element.tag == "row":
                    print("ROW FIELDS:", [c.tag for c in element])
                    break

    except Exception as exc:
        print("ERROR:", exc)
