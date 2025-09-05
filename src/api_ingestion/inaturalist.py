from io import BytesIO
import os
import pandas as pd
from pyinaturalist import get_observations
from pyinaturalist_convert import to_dataframe

from src.utils.logging_utils import setup_logger
from src.utils.date_utils import get_current_utc_timestamp
from src.utils.storage_utils import upload_parquet_to_minio
from src.config.app_settings import (
    LOG_FILE,
    CA_BIRD_HOTSPOTS,
    BIRDS_TAXON_NAME
)

log_name = os.path.basename(__file__)
logger = setup_logger(log_name, LOG_FILE)

def get_inaturalist_observations_by_location(
        latitude, 
        longitude, 
        radius_km, 
        start_date, 
        end_date, 
        per_page=200):
    """GET bird observations from iNaturalist API for a specific location and date range."""

    logger.info(f'Fetching bird observations from iNaturalist API for location ({latitude}, {longitude}) within radius {radius_km} km '
                f'from {start_date} to {end_date}')

    try:
        observations = get_observations(
            taxon_name=BIRDS_TAXON_NAME,
            latitude=latitude,
            longitude=longitude,
            radius=radius_km,
            d1=start_date,
            d2=end_date,
            per_page=per_page,
            only_id=False, # Get full observation details or not
            geo=False,  # Include geo tagged data or not - including for raw, will filter later
            verifiable=False, # Include research-grade observations or not
            order_by='observed_on',
            order='desc',
            sounds=False, # Exclude sounds-only observations,
            captive=False   # Exclude zoo/captive observations
        )
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

    hotspot_name = 'point_reyes'
    hotspot_data = CA_BIRD_HOTSPOTS[hotspot_name] 
    latitude = hotspot_data['latitude']
    longitude = hotspot_data['longitude']
    radius_km = hotspot_data['radius_km']
    start_date = '2024-07-01'
    end_date = '2024-07-31'

    logger.info(f'Fetching iNaturalist API recent observation data for hotspot: {hotspot_name}')
    observations = get_inaturalist_observations_by_location(
        latitude,
        longitude,
        radius_km,
        start_date,
        end_date
    )

    logger.info(f'Converting observations JSON data to parquet bytes')
    parquet_bytes = convert_json_to_parquet_bytes(observations)
    
    logger.info(f'Uploading observations Parquet data to MinIO')
    object_name=f'birds/inaturalist/observations/US-CA/{hotspot_name}/{start_date}_{end_date}.parquet'
    upload_parquet_to_minio(parquet_bytes, object_name=object_name, logger=logger)


if __name__ == "__main__":
    main()