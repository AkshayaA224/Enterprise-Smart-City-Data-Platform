WITH expected_hours AS (
    SELECT generate_series(0, 23) AS hour_num
),
per_record AS (
    SELECT
        source_record_id,
        COUNT(DISTINCT EXTRACT(HOUR FROM hour_start)) AS loaded_hours
    FROM warehouse.fact_traffic_volume
    GROUP BY source_record_id
)
SELECT
    COUNT(*) AS source_records,
    COUNT(*) FILTER (WHERE loaded_hours = 24) AS complete_records,
    COUNT(*) FILTER (WHERE loaded_hours < 24) AS incomplete_records,
    MIN(loaded_hours) AS minimum_hours,
    MAX(loaded_hours) AS maximum_hours
FROM per_record;