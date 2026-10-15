
import csv
import getpass
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import psycopg2
from psycopg2.extras import Json

RAW = Path("data/raw")
BATCH_SIZE = 1000

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


def file_fingerprint(path):
    digest = hashlib.sha256()

    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def verify_source_baseline(conn, dataset, filename, fingerprint):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT source_filename, source_fingerprint
            FROM audit.source_file_baselines
            WHERE dataset_name = %s
            """,
            (dataset,),
        )
        baseline = cur.fetchone()

    if baseline is None:
        raise ValueError(
            f"No approved fingerprint baseline for {dataset}"
        )

    approved_filename, approved_fingerprint = baseline

    if approved_filename != filename:
        raise ValueError(
            f"Filename mismatch: expected {approved_filename}, "
            f"got {filename}"
        )

    if approved_fingerprint != fingerprint:
        raise ValueError(
            "Source fingerprint mismatch. Review and approve "
            "the new source version before ingestion."
        )


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
        raise ValueError("Unrecognized JSON record structure.")
    else:
        raise ValueError("Unsupported JSON root type.")


def xml_records(path):
    for _, element in ET.iterparse(path, events=("end",)):
        if element.tag == "row":
            yield {
                child.tag: child.text or ""
                for child in element
            }
            element.clear()


def get_records(path, file_format):
    if file_format == "csv":
        return csv_records(path)
    if file_format == "json":
        return json_records(path)
    if file_format == "xml":
        return xml_records(path)

    raise ValueError(f"Unsupported format: {file_format}")


def record_key(dataset, row, row_number):
    # These datasets may contain legitimate repeated records.
    row_based = {
        "emergency",
        "parking",
        "property_tax",
        "traffic",
    }

    if dataset in row_based:
        return f"source:row:{row_number:09d}"

    key_fields = {
        "citizen_services": ["objectid"],
        "electricity": ["Entity", "Year"],
        "environment": ["Unique ID"],
        "transport": ["service_date", "day_type"],
        "waste": ["MONTH", "BOROUGH", "COMMUNITYDISTRICT"],
        "water": ["cnty_fips"],
    }

    fields = key_fields.get(dataset, [])
    values = [
        str(row.get(field, "") or "").strip()
        for field in fields
    ]

    if fields and all(values):
        return "key:" + json.dumps(
            values, ensure_ascii=False, separators=(",", ":")
        )

    return f"source:row:{row_number:09d}"


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
                fingerprint = file_fingerprint(path)

                verify_source_baseline(
                    conn, dataset, filename, fingerprint
                )

                # Commit the RUNNING audit entry separately.
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO audit.ingestion_runs
                                (dataset_name, ingestion_type, status,
                                 source_fingerprint)
                            VALUES (%s, 'BATCH', 'RUNNING', %s)
                            RETURNING run_id
                            """,
                            (dataset, fingerprint),
                        )
                        run_id = cur.fetchone()[0]

                batch = []

                def flush_batch():
                    nonlocal rows_loaded

                    if not batch:
                        return

                    batch_loaded = 0

                    # Each batch and its progress update commit together.
                    with conn:
                        with conn.cursor() as cur:
                            for row_number, row in batch:
                                if not isinstance(row, dict):
                                    raise ValueError(
                                        f"Expected a dictionary record, "
                                        f"got {type(row).__name__}"
                                    )

                                source_id = record_key(
                                    dataset, row, row_number
                                )

                                cur.execute(
                                    f"""
                                    INSERT INTO staging.{dataset}
                                        (source_data, source_record_id)
                                    VALUES (%s, %s)
                                    ON CONFLICT (source_record_id)
                                    WHERE source_record_id IS NOT NULL
                                    DO NOTHING
                                    """,
                                    (Json(row), source_id),
                                )

                                batch_loaded += cur.rowcount

                            new_total = rows_loaded + batch_loaded

                            cur.execute(
                                """
                                UPDATE audit.ingestion_runs
                                SET rows_read = %s,
                                    rows_loaded = %s
                                WHERE run_id = %s
                                """,
                                (rows_read, new_total, run_id),
                            )

                    rows_loaded += batch_loaded
                    batch.clear()

                records = get_records(path, file_format)

                for row_number, row in enumerate(records, start=1):
                    rows_read += 1
                    batch.append((row_number, row))

                    if len(batch) >= BATCH_SIZE:
                        flush_batch()

                # Load the final batch, even if it has fewer than 1,000 rows.
                flush_batch()

                # Check that the source did not change during ingestion.
                final_fingerprint = file_fingerprint(path)

                if final_fingerprint != fingerprint:
                    raise ValueError(
                        "Source file changed during ingestion. "
                        "Review the file before rerunning."
                    )

                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE audit.ingestion_runs
                            SET status = 'SUCCESS',
                                rows_read = %s,
                                rows_loaded = %s,
                                completed_at = CURRENT_TIMESTAMP,
                                error_message = NULL
                            WHERE run_id = %s
                            """,
                            (rows_read, rows_loaded, run_id),
                        )

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
                            cur.execute(
                                """
                                UPDATE audit.ingestion_runs
                                SET status = 'FAILED',
                                    rows_read = %s,
                                    rows_loaded = %s,
                                    error_message = %s,
                                    completed_at = CURRENT_TIMESTAMP
                                WHERE run_id = %s
                                """,
                                (
                                    rows_read,
                                    rows_loaded,
                                    str(exc)[:4000],
                                    run_id,
                                ),
                            )

                print(
                    f"FAILED {dataset}: {exc}; "
                    f"read={rows_read}, committed={rows_loaded}"
                )

    finally:
        conn.close()


if __name__ == "__main__":
    main()
