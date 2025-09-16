CREATE OR REPLACE VIEW bronze.raw_open_meteo AS
SELECT *
FROM read_parquet('s3://raw/weather/general/source=open-meteo/region=US-CA/frequency=daily/date=*/grid_size=*/tile=*/*.parquet')