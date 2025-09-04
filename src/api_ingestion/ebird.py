import os
import requests
from io import BytesIO
import pandas as pd

from src.utils.logging_utils import setup_logger
from src.utils.date_utils import get_current_utc_timestamp
from src.utils.storage_utils import connect_to_minio
from src.config.app_settings import (
    LOG_FILE,
    EBIRD_API_KEY, 
    EBIRD_BASE_URL,
    MINIO_BUCKET_NAME,
    EBIRD_REGION_CODE
)

log_name = os.path.basename(__file__)
logger = setup_logger(log_name, LOG_FILE)

def get_recent_observations_by_region(region_code, base_url=EBIRD_BASE_URL, api_key=EBIRD_API_KEY, query_params=None):
    logger.info(f'Fetching recent observations for region: "{region_code}"')
    if query_params is None:
        query_params = {}

    headers = {
        'X-ebirdApiToken': api_key
    }

    recent_observations_by_region_endpoint = f'data/obs/{region_code}/recent'
    url = f'{base_url}/{recent_observations_by_region_endpoint}'

    try:
        response = requests.get(url, headers=headers, params=query_params)
        response.raise_for_status()
        logger.info(f'Successfully fetched data for region: "{region_code}" at url: {url} with query params: {query_params if query_params else "{}"}')
    except requests.exceptions.RequestException as e:
        logger.error(f'Error fetching data from eBird API: {e}')
        raise

    return response.json()

def convert_json_to_parquet(data):
    bird_data = pd.DataFrame(data)
    buffer = BytesIO()
    bird_data.to_parquet(buffer, index=False)
    buffer.seek(0)
    return buffer

def upload_parquet_to_minio(data, object_name):
    logger.info(f'Connecting to MinIO client')
    minio_client = connect_to_minio()
    if minio_client:
        logger.info(f'Connected to MinIO client')
    else:
        logger.error(f'Failed to connect to MinIO client')
        return

    try:
        minio_client.put_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=object_name,
            data=data,
            length=data.getbuffer().nbytes,
            content_type='application/parquet'
        )
        logger.info(f'Successfully uploaded {object_name} to MinIO')
    except Exception as e:
        logger.error(f'Error uploading to MinIO: {e}')
        raise

def main():
    logger.info('Starting eBird API ingestion')
    timestamp = get_current_utc_timestamp('%Y%m%d_%H%M%S')
    
    logger.info(f'Fetching eBird API recent observation data')
    # build CO url
    region_code = EBIRD_REGION_CODE
    query_params = {
        # 'maxResults': 10,
        'back': 30
    }

    try:
        logger.info('Fetching recent CO observations')
        co_observations = get_recent_observations_by_region(region_code, query_params=query_params)
    except Exception as e:
        logger.error(f'Error fetching eBird API data: {e}')
        raise

    logger.info(f'Converting eBird API data to Parquet format')
    co_observations_parquet = convert_json_to_parquet(co_observations)
    logger.info(f'Uploading Parquet file to MinIO')
    object_name=f'bird_watching/ebird/observations/recent/{region_code}_{timestamp}.parquet'
    upload_parquet_to_minio(co_observations_parquet, object_name=object_name)


if __name__ == "__main__":
    main()