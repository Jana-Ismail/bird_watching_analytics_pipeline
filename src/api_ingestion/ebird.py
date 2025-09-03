import os
import requests
from io import BytesIO
import pandas as pd

from src.utils.logging_utils import setup_logger
from src.config.app_settings import (
    LOG_FILE,
    EBIRD_API_KEY, 
    EBIRD_OBSERVATION_BASE_URL
)

log_name = os.path.basename(__file__)
logger = setup_logger(log_name, LOG_FILE)

def get_recent_observations_by_region(region_code, base_url=EBIRD_OBSERVATION_BASE_URL, api_key=EBIRD_API_KEY, query_params=None):
    logger.info(f'Fetching recent observations for region: "{region_code}"')
    if query_params is None:
        query_params = {}

    headers = {
        'X-ebirdApiToken': api_key
    }

    url = f'{base_url}/{region_code}/recent'

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

def main():
    logger.info('Starting eBird API ingestion')
    
    logger.info(f'Fetching eBird API recent observation data')
    # build CO url
    region_code = 'US-CO'
    query_params = {
        'maxResults': 10,
        'back': 7
    }
    co_observations = get_recent_observations_by_region(region_code, query_params=query_params)



if __name__ == "__main__":
    main()