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
    BIRDS_TAXON_NAME,
    MINIO_RAW_BUCKET_NAME,
    CA_HOTSPOTS_BY_CENTER_POINT_COORDINATES,
    CA_REGION_CODE
)

log_name = os.path.basename(__file__)
logger = setup_logger(log_name, LOG_FILE)

CA_PLACE_ID = 14

def get_inaturalist_observations_by_coordinates(
        latitude, 
        longitude, 
        radius_km, 
        start_date, 
        end_date, 
        per_page=200):
    """GET bird observations from iNaturalist API for a specific location and date range."""

    logger.info(f'Fetching bird observations from iNaturalist API for location ({latitude}, {longitude}) within radius {radius_km} km '
                f'from {start_date} to {end_date}')
    
    observations = []
    page = 1
    total_results = None

    while total_results is None or len(observations) < total_results:
        try:
            response = get_observations(
                taxon_name=BIRDS_TAXON_NAME,
                place_id=CA_PLACE_ID,
                # lat=latitude,
                # lng=longitude,
                # radius=radius_km,
                page=page,
                d1=start_date,
                d2=end_date,
                per_page=per_page,
                only_id=False,
                geo=True, # Set to True to enable geographic filtering
                verifiable=False,
                order_by='observed_on',
                order='desc',
                sounds=False,
                captive=False
            )
            
            results = response.get('results', [])
            total_results = response.get('total_results', 0)
            
            if not results:
                logger.info(f"No results found on page {page}. Ending pagination.")
                break
            
            observations.extend(results)
            logger.info(f"Fetched {len(results)} observations on page {page}. Total fetched: {len(observations)} of {total_results}.")
            page += 1

            if len(observations) >= total_results:
                break
        
        except Exception as e:
            logger.error(f'Error fetching observations from iNaturalist API: {e}')
            raise

    return observations

def convert_json_to_parquet_bytes(data, timestamp):
    logger.info('Converting JSON data to Parquet format using Pandas')

    try:
        observations = to_dataframe(data)

        if observations.empty:
            logger.warning('No observations to convert. Returning empty buffer.')
            return BytesIO()
        
        observations['_source'] = 'iNaturalist API'
        observations['_ingested_at_utc'] = timestamp
        observations['_source_base_url'] = 'https://api.inaturalist.org/v1/observations'

        # Normalize datetime columns
        for col in ['observed_on', 'created_at', 'updated_at']:
            if col in observations.columns:
                observations[col] = pd.to_datetime(
                    observations[col],
                    errors='coerce',
                    utc=True
                )

        parquet_buffer = BytesIO()
        observations.to_parquet(parquet_buffer, engine="pyarrow", index=False)
        parquet_buffer.seek(0)
        logger.info('Successfully converted observations to Parquet bytes')
        
        return parquet_buffer
    
    except Exception as e:
        logger.error(f'Error converting observations to Parquet bytes: {e}')
        raise

def main():
    timestamp = get_current_utc_timestamp('%Y-%m-%dT%H:%M:%S')
    logger.info(f'Starting iNaturalist API ingestion at {timestamp}')
    target_year = 2017

    for hotspot_name, hotspot_data in CA_HOTSPOTS_BY_CENTER_POINT_COORDINATES.items():
        latitude, longitude = hotspot_data.split(',')
        latitude = float(latitude)
        longitude = float(longitude)

        radius_km = 200
        start_date = f'{target_year}-01-01'
        end_date = f'{target_year}-12-31'

        logger.info(f'Fetching iNaturalist API recent observation data for hotspot: {hotspot_name} from {start_date} to {end_date}')
        observations = get_inaturalist_observations_by_coordinates(
            latitude,
            longitude,
            radius_km,
            start_date,
            end_date
        )
        logger.info(f'Fetched {len(observations)} total observations for hotspot: {hotspot_name} in {target_year}')

        if observations:
            logger.info('Converting observations JSON data to parquet bytes')
            parquet_bytes = convert_json_to_parquet_bytes(observations, timestamp)
        
            logger.info('Uploading observations Parquet data to MinIO')
            file_name = f'inaturalist_observations_{CA_REGION_CODE}_{hotspot_name}_{target_year}.parquet'
            object_name=f'birds/observations/source=inaturalist/region={CA_REGION_CODE}/hotspot={hotspot_name}/frequency=yearly/date={target_year}/{file_name}'
            upload_parquet_to_minio(parquet_bytes, object_name=object_name, bucket_name=MINIO_RAW_BUCKET_NAME, logger=logger)
        else:
            logger.warning(f'No observations found for hotspot: {hotspot_name} in {target_year}. Skipping Parquet conversion and upload.')

if __name__ == "__main__":
    main()