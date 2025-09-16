CREATE OR REPLACE TABLE silver.clean_ebird AS
SELECT *
FROM (
    SELECT
        speciesCode AS species_code,
        comName AS common_name,
        sciName AS scientific_name,
        locId AS location_id,
        locName AS location_name,
        CAST(obsDt AS TIMESTAMP) AS observation_datetime,
        CAST(obsDt AS DATE) AS observation_date,
        CAST(howMany AS INT) AS individual_count,
        CAST(lat AS DOUBLE) AS latitude,
        CAST(lng AS DOUBLE) AS longitude,
        CAST(obsValid AS BOOLEAN) AS is_valid,
        CAST(obsReviewed AS BOOLEAN) AS is_reviewed,
        CAST(locationPrivate AS BOOLEAN) AS is_private,
        subId AS submission_id,
        _source,
        _source_url,
        CAST(_ingested_at_utc AS TIMESTAMP) AS ingested_at_utc,
        CAST(date AS DATE) AS obs_date,
        ROW_NUMBER() OVER (PARTITION BY subId ORDER BY _ingested_at_utc DESC) AS row_num
FROM bronze.raw_ebird
) subquery
WHERE row_num = 1;