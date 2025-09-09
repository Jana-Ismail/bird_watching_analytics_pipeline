from io import BytesIO, StringIO
from duckdb import df
import pandas as pd
import requests
import time
from datetime import datetime, timedelta, timezone

from src.utils.logging_utils import setup_logger, get_log_name
from src.utils.date_utils import get_current_utc_timestamp
from src.utils.storage_utils import upload_parquet_to_minio
from src.config.app_settings import (
    LOG_FILE,
    CA_REGION_CODE,
    NASA_FIRMS_API_KEY,
    NASA_FIRMS_BASE_URL,
    NASA_FIRMS_DATA_SOURCE,
    CA_BBOX_COORDINATES,
    MINIO_RAW_BUCKET_NAME
)

logger = setup_logger(get_log_name(__file__), LOG_FILE)

def fetch_nasa_firms_daily(url, date, timeout=20):
    """Fetch daily NASA FIRMS data for a specific date."""
    logger.info(f'Fetching NASA FIRMS data for date: {date}')
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        fire_data = pd.read_csv(StringIO(response.text))
        logger.info(f'fetched {len(fire_data)} records for date: {date}')
        return fire_data
    except requests.Timeout:
        logger.error(f'Request timed out after {timeout} seconds')
    except requests.RequestException as e:
        logger.error(f'Error fetching NASA FIRMS data for date {date}: {e}')
    except Exception as e:
        logger.error(f'Unexpected error: {e}')

def convert_csv_to_parquet(data):
    """Convert a DataFrame to a parquet BytesIO buffer."""
    buffer = BytesIO()
    data.to_parquet(buffer, index=False)
    buffer.seek(0)
    return buffer

def main():

    timestamp = get_current_utc_timestamp('%Y%m%d_%H%M%S')
    logger.info(f'Starting NASA FIRMS DAILY ingestion at {timestamp}')

    # Get yesterday's date in UTC (timezone-aware) and format as 'YYYY-MM-DD'
    target_date_str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')

    url = f'{NASA_FIRMS_BASE_URL}/{NASA_FIRMS_API_KEY}/{NASA_FIRMS_DATA_SOURCE}/{CA_BBOX_COORDINATES}/1/{target_date_str}'

    fire_data = fetch_nasa_firms_daily(url, target_date_str)

    if fire_data is None or fire_data.empty:
        logger.info('No data to upload.')
        return
    
    parquet_buffer = convert_csv_to_parquet(fire_data)

    file_name = f'nasa_firms_fire_{CA_REGION_CODE}_{target_date_str}_{timestamp}.parquet'
    object_name = f'weather/fire/source=nasa_firms/daily/region={CA_REGION_CODE}/date={target_date_str}/{file_name}'

    upload_parquet_to_minio(parquet_buffer, object_name=object_name, bucket_name=MINIO_RAW_BUCKET_NAME, logger=logger)

if __name__ == '__main__':
    main()
