import csv
import getpass
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import psycopg2
from psycopg2.extras import Json

RAW = Path("data/raw")
BATCH_SIZE = 100

DATASETS = {
    "citizen_services": ("citizen_services.csv", "csv"),
    "electricity": ("electricity.csv", "csv"),
    "emergency": ("emergency.xml", "xml"),
    "environment": ("environment.csv", "csv"),
    "parking": ("parking.json", "json"),
    "property_tax": ("property_tax.csv", "csv"),
    "traffic": ("traffic.csv", "csv"),
    "transport": ("transport.csv", "csv"),
    "waste": ("waste.csv", "csv"),
    "water": ("water.csv", "csv"),
}

def csv_records(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f)

def json_records(path):
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if isinstance(data, list):
        yield from data
    elif isinstance(data, dict):
        for key in ("data", "records", "results"):
            if isinstance(data.get(key), list):
                yield from data[key]
                return
        raise ValueError(
            "JSON structure is not a list or a recognized records container."
        )
    else:
        raise ValueError("Unsupported JSON root type.")

def xml_records(path):
    # This source uses <response><rows><row>...</row></rows></response>.
    for event, element in ET.iterparse(path, events=("end",)):
        if element.tag == "row":
            yield {child.tag: child.text for child in element}
            element.clear()

def record_key(dataset, row):
    key_fields = {
        "citizen_services": ["objectid"],
        "electricity": ["Entity", "Code", "Year"],
        "property_tax": ["PARID", "YEAR"],
        "traffic": ["ID"],
        "transport": ["service_date", "day_type"],
        "waste": ["MONTH", "BOROUGH", "COMMUNITYDISTRICT"],
        "water": ["cnty_fips", "state"],
    }.get(dataset)

    if key_fields and all(
        row.get(field) not in (None, "")
        for field in key_fields
    ):
        return "|".join(str(row[field]).strip() for field in key_fields)

    import hashlib
    import json

    raw_key = json.dumps(
        row, sort_keys=True, ensure_ascii=False, default=str
    )
    return hashlib.sha256(
        f"{dataset}|{raw_key}".encode("utf-8")
    ).hexdigest()
def main():
    password = getpass.getpass("PostgreSQL password: ")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="smart_city_platform",
        user="postgres",
        password=password,
    )

    try:
        for dataset, (filename, file_format) in DATASETS.items():
            path = RAW / filename
            if not path.exists():
                print(f"SKIPPED {dataset}: file not found")
                continue

            run_id = None
            rows_read = 0
            rows_loaded = 0

            try:
                if file_format == "csv":
                    records = csv_records(path)
                elif file_format == "json":
                    records = json_records(path)
                elif file_format == "xml":
                    records = xml_records(path)
                else:
                    raise ValueError(f"Unsupported format: {file_format}")

                with conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO audit.ingestion_runs
                                (dataset_name, ingestion_type, status)
                            VALUES (%s, 'BATCH', 'RUNNING')
                            RETURNING run_id
                        """, (dataset,))
                        run_id = cur.fetchone()[0]

                        for row in records:
                            if rows_read >= BATCH_SIZE:
                                break

                            if not isinstance(row, dict):
                                raise ValueError(
                                   f"Expected object/record, got {type(row).__name__}"
                                )

                            rows_read += 1

                            source_id = record_key(dataset, row)
                            cur.execute(f"""
                                INSERT INTO staging.{dataset}
                                    (source_data, source_record_id)
                                VALUES (%s, %s)
                                ON CONFLICT (source_record_id)
                                WHERE source_record_id IS NOT NULL
                                DO NOTHING
                            """, (Json(row), source_id))

                            rows_loaded += cur.rowcount

                        cur.execute("""
                            UPDATE audit.ingestion_runs
                            SET status = 'SUCCESS',
                                rows_read = %s,
                                rows_loaded = %s,
                                completed_at = CURRENT_TIMESTAMP
                            WHERE run_id = %s
                        """, (rows_read, rows_loaded, run_id))

                print(
                    f"SUCCESS {dataset}: read={rows_read}, "
                    f"inserted={rows_loaded}, "
                    f"skipped={rows_read - rows_loaded}"
                )

            except Exception as exc:
                conn.rollback()
                if run_id is not None:
                    with conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE audit.ingestion_runs
                                SET status = 'FAILED',
                                    rows_read = %s,
                                    rows_loaded = %s,
                                    error_message = %s,
                                    completed_at = CURRENT_TIMESTAMP
                                WHERE run_id = %s
                            """, (rows_read, rows_loaded, str(exc), run_id))
                print(f"FAILED {dataset}: {exc}")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
