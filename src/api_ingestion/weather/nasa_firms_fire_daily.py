from io import BytesIO, StringIO
from duckdb import df
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone

from src.utils.logging_utils import setup_logger, get_log_name
from src.utils.date_utils import get_current_utc_timestamp
from src.utils.storage_utils import upload_parquet_to_minio
from src.utils.file_utils import convert_data_to_parquet
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
        # fire_data = response.content

        logger.info(f'fetched {len(fire_data)} records for date: {date}')
        return fire_data
    
    except requests.Timeout:
        logger.error(f'Request timed out after {timeout} seconds')

    except requests.RequestException as e:
        logger.error(f'Error fetching NASA FIRMS data for date {date}: {e}')

    except Exception as e:
        logger.error(f'Unexpected error: {e}')


def process_nasa_firms_data(data, url, timestamp, target_date):
    """Process and upload NASA FIRMS data to MinIO as Parquet."""
    logger.info(f'Starting to process NASA FIRMS data for upload to MinIO at ingestion time: {timestamp}')

    metadata = {
        '_source': 'NASA FIRMS API',
        '_source_url': url,
        '_ingested_at_utc': timestamp,
    }

    logger.info(f'Converting NASA FIRMS data to Parquet for upload to MinIO at ingestion time: {timestamp}')
    parquet_buffer = convert_data_to_parquet(data, metadata_columns=metadata)

    logger.info(f'Uploading NASA FIRMS data to MinIO at ingestion time: {timestamp}')
    file_name = f'nasa-firms_fire_{CA_REGION_CODE}_{target_date}.parquet'
    object_name = f'weather/fire/source=nasa-firms/region={CA_REGION_CODE}/frequency=daily/date={target_date}/{file_name}'
    try:
        upload_parquet_to_minio(parquet_buffer, object_name=object_name, bucket_name=MINIO_RAW_BUCKET_NAME, logger=logger)
        logger.info(f'Successfully uploaded NASA FIRMS data to MinIO at ingestion time: {timestamp} from url: "{url}"')
    except Exception as e:
        logger.error(f'Error uploading NASA FIRMS data to MinIO at ingestion time: {timestamp}: {e}')
        raise


def main():

    timestamp = get_current_utc_timestamp('%Y-%m-%dT%H:%M:%S')
    logger.info(f'Starting NASA FIRMS DAILY ingestion at {timestamp}')

    target_date = (datetime.now(timezone.utc) - timedelta(days=3)).strftime('%Y-%m-%d')
    url = f'{NASA_FIRMS_BASE_URL}/{NASA_FIRMS_API_KEY}/{NASA_FIRMS_DATA_SOURCE}/{CA_BBOX_COORDINATES}/1/{target_date}'

    try:
        fire_data = fetch_nasa_firms_daily(url, target_date)
    except Exception as e:
        logger.error(f'Error fetching NASA FIRMS data: {e}')
        return

    if fire_data is None or fire_data.empty:
        logger.error('No data to upload.')
    else:
        process_nasa_firms_data(fire_data, url, timestamp, target_date)


if __name__ == '__main__':
    main()
