import getpass
from pathlib import Path

import psycopg2

from importlib.util import spec_from_file_location, module_from_spec

spec = spec_from_file_location(
    "batch_ingest", "python/05_batch_ingest.py"
)
module = module_from_spec(spec)
spec.loader.exec_module(module)

password = getpass.getpass("PostgreSQL password: ")

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="smart_city_platform",
    user="postgres",
    password=password,
)

try:
    for dataset, (filename, file_format) in module.DATASETS.items():
        path = module.RAW / filename

        if not path.exists():
            print(f"FAIL {dataset}: file missing")
            continue

        fingerprint = module.file_fingerprint(path)

        try:
            module.verify_source_baseline(
                conn, dataset, filename, fingerprint
            )
            print(f"PASS {dataset}: baseline matches")
        except Exception as exc:
            print(f"FAIL {dataset}: {exc}")
finally:
    conn.close()