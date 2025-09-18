CREATE OR REPLACE TABLE silver.clean_nasa_firms AS
SELECT *
FROM (
    SELECT
        CAST(latitude AS DOUBLE) AS latitude,
        CAST(longitude AS DOUBLE) AS longitude,
        CAST(brightness AS DOUBLE) AS brightness,
        CAST(scan AS DOUBLE) AS scan_km,
        CAST(track AS DOUBLE) AS track_km,
        CAST(acq_date AS DATE) AS acquisition_date,
        CAST(acq_time AS VARCHAR) AS acquisition_time,
        satellite,
        instrument,
        CAST(confidence AS INT) AS confidence,
        version,
        CAST(bright_t31 AS DOUBLE) AS brightness_t31,
        CAST(frp AS DOUBLE) AS fire_radiative_power,
        daynight AS daynight_flag,
        _source,
        _source_url,
        CAST(_ingested_at_utc AS TIMESTAMP) AS _ingested_at_utc,
        ROW_NUMBER() OVER (PARTITION BY latitude, longitude, acquisition_date, acquisition_time ORDER BY _ingested_at_utc DESC) AS row_num
    FROM bronze.raw_nasa_firms
) subquery
WHERE row_num = 1;
