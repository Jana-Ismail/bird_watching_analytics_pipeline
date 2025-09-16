CREATE OR REPLACE VIEW bronze.raw_nasa_firms AS
SELECT *
FROM read_parquet('s3://raw/weather/fire/source=nasa-firms/region=US-CA/frequency=daily/date=*/*.parquet')