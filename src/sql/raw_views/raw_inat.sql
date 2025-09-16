CREATE OR REPLACE VIEW bronze.raw_inat_daily AS
SELECT
    uuid,
    id,
    species_guess,
    taxon,
    observed_on,
    place_guess,
    identifications_count,
    quality_grade,
    reviewed_by,
    uri,
    _source,
    _source_url,
    _total_results,
    _ingested_at_utc
FROM read_parquet(
    's3://raw/birds/observations/source=inaturalist/region=US-CA/hotspot=*/frequency=*/date=*/*.parquet',
    union_by_name = true
);
