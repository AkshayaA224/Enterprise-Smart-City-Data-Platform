
import getpass
from pathlib import Path

import psycopg2

REPORT_TABLE = "quality.data_quality_summary"

# Dataset, JSON field, staging table
CHECKS = [
    ("citizen_services", "address", "citizen_services"),
    ("citizen_services", "status", "citizen_services"),
    ("electricity", "Entity", "electricity"),
    ("electricity", "Year", "electricity"),
    ("environment", "Name", "environment"),
    ("environment", "Data Value", "environment"),
    ("emergency", "location", "emergency"),
    ("emergency", "incident_type", "emergency"),
    ("parking", "Parking_Spot_ID", "parking"),
    ("parking", "Occupancy_Status", "parking"),
    ("property_tax", "PARID", "property_tax"),
    ("property_tax", "YEAR", "property_tax"),
    ("traffic", "ID", "traffic"),
    ("traffic", "Date", "traffic"),
    ("transport", "service_date", "transport"),
    ("transport", "total_rides", "transport"),
    ("waste", "MONTH", "waste"),
    ("waste", "BOROUGH", "waste"),
    ("water", "cnty_fips", "water"),
    ("water", "county", "water"),
]


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
        results = []

        with conn.cursor() as cur:
            for dataset, field, table in CHECKS:
                query = f"""
                    SELECT
                        COUNT(*),
                        COUNT(*) FILTER (
                            WHERE NULLIF(
                                BTRIM(source_data->>%s), ''
                            ) IS NULL
                        )
                    FROM staging.{table}
                """

                cur.execute(query, (field,))
                total_rows, missing_rows = cur.fetchone()

                missing_percentage = (
                    round(missing_rows * 100 / total_rows, 3)
                    if total_rows else 0
                )

                results.append(
                    (
                        dataset,
                        field,
                        total_rows,
                        missing_rows,
                        missing_percentage,
                    )
                )

        # Replace the previous report with freshly calculated results.
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"DELETE FROM {REPORT_TABLE}"
                )

                cur.executemany(
                    f"""
                    INSERT INTO {REPORT_TABLE}
                        (dataset_name, field_name, total_rows,
                         missing_rows, missing_percentage, checked_at)
                    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """,
                    results,
                )

        print("\nDATA QUALITY REPORT")
        print("-" * 65)

        for dataset, field, total, missing, percentage in results:
            print(
                f"{dataset:20} | {field:20} | "
                f"total={total:8} | missing={missing:8} "
                f"({percentage:.3f}%)"
            )

        print(f"\nReport refreshed: {len(results)} field checks.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
