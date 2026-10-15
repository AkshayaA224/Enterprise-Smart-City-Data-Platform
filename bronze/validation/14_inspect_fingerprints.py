
import hashlib
from pathlib import Path

RAW = Path("data/raw")

FILES = [
    "citizen_services.csv",
    "electricity.csv",
    "emergency.xml",
    "environment.csv",
    "parking.json",
    "property_tax.csv",
    "traffic.csv",
    "transport.csv",
    "waste.csv",
    "water.csv",
]


def fingerprint(path):
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


for filename in FILES:
    path = RAW / filename

    if not path.exists():
        print(f"MISSING: {filename}")
        continue

    print(
        f"{filename} | "
        f"bytes={path.stat().st_size} | "
        f"sha256={fingerprint(path)}"
    )
