CREATE VIEW IF NOT EXISTS bird_ducklake.bronze.raw_ebird AS
SELECT *
FROM read_parquet('s3://raw/birds/observations/source=ebird/region=US-CA/frequency=daily/date=*/*.parquet');