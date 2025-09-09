from io import BytesIO
import os
import pandas as pd
from pyinaturalist import get_observations
from pyinaturalist_convert import to_dataframe

# from api_ingestion.inaturalist_historical import get_inaturalist_observations_by_location
from src.utils.logging_utils import setup_logger
from src.utils.date_utils import get_current_utc_timestamp, get_pacific_day_range_for_inat
from src.utils.storage_utils import upload_parquet_to_minio
from src.config.app_settings import (
    LOG_FILE,
    CA_REGION_CODE,
    CA_HOTSPOTS_BY_CENTER_POINT_COORDINATES,
    BIRDS_TAXON_NAME,
    MINIO_RAW_BUCKET_NAME
)

log_name = os.path.basename(__file__)
logger = setup_logger(log_name, LOG_FILE)

def get_inaturalist_observations_by_coordinates(
        latitude, 
        longitude, 
        radius_km, 
        start_date, 
        end_date, 
        per_page=200
    ):
    """GET bird observations from iNaturalist API for a specific location, km radius, and date range."""

    logger.info(
        f'Fetching bird observations from iNaturalist API for location ({latitude}, {longitude}) '
        f'within radius {radius_km} km from {start_date} to {end_date}'
    )

    observations = []
    page = 1
    while True:
        try:
            response = get_observations(
                taxon_name=BIRDS_TAXON_NAME,
                latitude=latitude,
                longitude=longitude,
                radius=radius_km,
                d1=start_date,
                d2=end_date,
                per_page=per_page,
                page=page,
                only_id=False,
                verifiable=False,
                order_by='observed_on',
                order='desc',
                sounds=False,
                captive=False
            )
            
            results = response.get('results', [])
            if not results:
                break

            observations.extend(results)
            page += 1
        except Exception as e:
            logger.error(f'Error fetching observations from iNaturalist API: {e}')
            raise

    return observations

def convert_json_to_parquet_bytes(data):
    logger.info('Converting JSON data to Parquet format using Pandas')

    try:
        # Convert JSON → DataFrame
        observations = to_dataframe(data)

        # Normalize datetime columns
        if 'observed_on' in observations.columns:
            observations['observed_on'] = pd.to_datetime(observations['observed_on'], errors='coerce', utc=True)

        parquet_buffer = BytesIO()
        # Write DataFrame to Parquet (in-memory)
        observations.to_parquet(parquet_buffer, engine="pyarrow", index=False)
        parquet_buffer.seek(0)

        logger.info('Successfully converted observations to Parquet bytes')
        return parquet_buffer

    except Exception as e:
        logger.error(f'Error converting observations to Parquet bytes: {e}')
        raise


def main():
    timestamp = get_current_utc_timestamp('%Y%m%d_%H%M%S')
    logger.info(f'Starting iNaturalist API ingestion at {timestamp}')

    for hotspot_name, hotspot_data in CA_HOTSPOTS_BY_CENTER_POINT_COORDINATES.items():
        latitude, longitude = hotspot_data.split(',')
        latitude = float(latitude)
        longitude = float(longitude)

        radius_km = 200
        start_date, end_date = get_pacific_day_range_for_inat()

        logger.info(f'Fetching iNaturalist API recent observation data for hotspot: {hotspot_name} on {start_date}')
        observations = get_inaturalist_observations_by_coordinates(
            latitude,
            longitude,
            radius_km,
            start_date,
            end_date
        )
        logger.info(f'Fetched {len(observations)} observations for hotspot: {hotspot_name} on {start_date}')
        logger.debug(f'Observations data sample: {observations[:2]}')  # Log first 2 observations for debugging

        logger.info(f'Converting observations JSON data to parquet bytes')
        parquet_bytes = convert_json_to_parquet_bytes(observations)
    
        logger.info(f'Uploading observations Parquet data to MinIO')
        file_name = f'inaturalist_observations_{CA_REGION_CODE}_{hotspot_name}_{start_date}_{timestamp}.parquet'
        object_name=f'birds/observations/region={CA_REGION_CODE}/hotspot={hotspot_name}/source=inaturalist/daily/date={start_date}/{file_name}'
        upload_parquet_to_minio(parquet_bytes, object_name=object_name, bucket_name=MINIO_RAW_BUCKET_NAME, logger=logger)


if __name__ == "__main__":
    main()