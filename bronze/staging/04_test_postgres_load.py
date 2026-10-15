import csv
import getpass
from pathlib import Path

import psycopg2
from psycopg2.extras import Json

SOURCE = Path("data/raw/citizen_services.csv")
BATCH_LIMIT = 100

def main():
    password = getpass.getpass("PostgreSQL password: ")

    if not SOURCE.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE}")

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        records = []

        for row in reader:
            records.append(row)
            if len(records) >= BATCH_LIMIT:
                break

    if not records:
        print("No source records found.")
        return

    missing_ids = [
        row for row in records
        if not row.get("objectid", "").strip()
    ]
    if missing_ids:
        raise ValueError(
            f"{len(missing_ids)} records have no objectid. "
            "Fix or quarantine them before loading."
        )

    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="smart_city_platform",
        user="postgres",
        password=password
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO audit.ingestion_runs
                        (dataset_name, ingestion_type, status, rows_read)
                    VALUES (%s, %s, %s, %s)
                    RETURNING run_id
                """, (
                    "citizen_services",
                    "BATCH_TEST",
                    "RUNNING",
                    len(records)
                ))
                run_id = cursor.fetchone()[0]

                cursor.executemany("""
                    INSERT INTO staging.citizen_services
                        (source_data, source_record_id)
                    VALUES (%s, %s)
                    ON CONFLICT (source_record_id)
                    WHERE source_record_id IS NOT NULL
                    DO NOTHING
                """, [
                    (Json(row), row["objectid"].strip())
                    for row in records
                ])

                inserted = cursor.rowcount

                cursor.execute("""
                    UPDATE audit.ingestion_runs
                    SET status = 'SUCCESS',
                        rows_loaded = %s,
                        completed_at = CURRENT_TIMESTAMP
                    WHERE run_id = %s
                """, (inserted, run_id))

        print(f"Run ID: {run_id}")
        print(f"Rows read: {len(records)}")
        print(f"New rows loaded: {inserted}")
        print(f"Existing rows skipped: {len(records) - inserted}")
        print("Status: SUCCESS")

    finally:
        connection.close()

if __name__ == "__main__":
    main()
