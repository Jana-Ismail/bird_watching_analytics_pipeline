import os
import requests

from src.utils.logging_utils import setup_logger
from src.utils.date_utils import get_current_utc_timestamp, get_pacific_target_date
from src.utils.storage_utils import upload_parquet_to_minio
from src.utils.file_utils import convert_data_to_parquet
from src.config.app_settings import (
    LOG_FILE,
    EBIRD_API_KEY, 
    EBIRD_BASE_URL,
    CA_REGION_CODE,
    MINIO_RAW_BUCKET_NAME
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

    return response.json(), url

def process_ebird_daily(data, region_code, target_date, timestamp, url):
    logger.info(f'Converting eBird API data to Parquet format')

    metadata = {
        '_source': 'eBird API',
        '_source_url': url,
        '_ingested_at_utc': timestamp,
    }

    observations_buffer = convert_data_to_parquet(data, metadata)

    logger.info(f'Uploading Parquet file to MinIO')
    file_name = f'ebird_observations_{region_code}.parquet'
    object_name=f'birds/observations/source=ebird/region={region_code}/frequency=daily/date={target_date}/{file_name}'
    upload_parquet_to_minio(observations_buffer, object_name=object_name, bucket_name=MINIO_RAW_BUCKET_NAME, logger=logger)

def main():
    timestamp = get_current_utc_timestamp('%Y-%m-%dT%H:%M:%S')

    target_date = get_pacific_target_date('%Y-%m-%d', days_ago=3)
    logger.info(f'Starting eBird API ingestion for {target_date}')

    logger.info(f'Fetching eBird API recent observation data')

    region_code = CA_REGION_CODE
    query_params = {
        'back': 1
    }

    try:
        logger.info('Fetching recent CA observations')
        observations, url = get_recent_observations_by_region(region_code, query_params=query_params)
    except Exception as e:
        logger.error(f'Error fetching eBird API data: {e}')
        raise

    if not observations:
        logger.warning(f'No recent observations found for region: "{region_code}"')
        return
    else:
        process_ebird_daily(observations, region_code, target_date, timestamp, url)



if __name__ == "__main__":
    main()