from io import BytesIO, StringIO
from duckdb import df
import pandas as pd
import requests
import time
from datetime import datetime, timedelta

from src.utils.logging_utils import setup_logger, get_log_name
from src.utils.date_utils import get_current_utc_timestamp
from src.utils.storage_utils import upload_parquet_to_minio
from src.config.app_settings import (
    LOG_FILE,
    NASA_FIRMS_API_KEY,
    NASA_FIRMS_BASE_URL,
    NASA_FIRMS_DATA_SOURCE,
    CA_COORDINATES,
    MINIO_RAW_BUCKET_NAME
)

logger = setup_logger(get_log_name(__file__), LOG_FILE)

CHUNK_SIZE_DAYS = 10

def fetch_firms_chunk(
        start_date, 
        end_date,
        base_url=NASA_FIRMS_BASE_URL,
        api_key=NASA_FIRMS_API_KEY,
        data_source=NASA_FIRMS_DATA_SOURCE,
        coordinates=CA_COORDINATES
    ):
    """Fetch a chunk of FIRMS fire data as a pandas DataFrame."""
    date_str = start_date.strftime('%Y-%m-%d')
    day_range = (end_date - start_date).days + 1
    url = f"{base_url}/{api_key}/{data_source}/{coordinates}/{day_range}/{date_str}"

    logger.info(f'Fetching FIRMS data for {date_str}, {day_range} days (source={data_source})')

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        if not response.text.strip():
            logger.info(f"No fire data returned for {date_str}")
            return pd.DataFrame()

        return pd.read_csv(StringIO(response.text))

    except requests.RequestException as e:
        logger.error(f'API request failed for {date_str}: {e}')
        return pd.DataFrame()
    except Exception as e:
        logger.error(f'Error parsing CSV for {date_str}: {e}')
        return pd.DataFrame()

def convert_csv_to_parquet(df: pd.DataFrame) -> BytesIO:
    """Convert a DataFrame to a parquet BytesIO buffer."""
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    return buffer

def process_nasa_firms_data(start_date_str, end_date_str, api_key, data_source=NASA_FIRMS_DATA_SOURCE):
    """
    Fetch FIRMS data in 10-day chunks and upload each chunk to MinIO.
    """
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    current_date = start_date
    request_count = 0

    while current_date <= end_date:
        chunk_end_date = min(current_date + timedelta(days=CHUNK_SIZE_DAYS - 1), end_date)

        fire_data = fetch_firms_chunk(current_date, chunk_end_date)
        if not fire_data.empty:
            parquet_buffer = convert_csv_to_parquet(fire_data)

            file_name = f"US-CA_{current_date.strftime('%Y%m%d')}_{chunk_end_date.strftime('%Y%m%d')}_{data_source.lower()}.parquet"
            object_name = (f'weather/fire/nasa_firms/{file_name}'
            )

            upload_parquet_to_minio(parquet_buffer, object_name, bucket_name=MINIO_RAW_BUCKET_NAME, logger=logger)

        # Respect API rate limits -> 5000 requests per 10 minutes
        if request_count > 0:
            time.sleep(1.2)

        current_date = chunk_end_date + timedelta(days=1)
        request_count += 1


def main():
    timestamp = get_current_utc_timestamp('%Y%m%d_%H%M%S')
    logger.info(f'Starting NASA FIRMS API ingestion at {timestamp}')


    start_date = '2024-07-01'
    end_date = '2024-07-31'

    logger.info(f'Processing NASA FIRMS data from {start_date} to {end_date}')
    process_nasa_firms_data(start_date, end_date, NASA_FIRMS_API_KEY, NASA_FIRMS_DATA_SOURCE)


if __name__ == "__main__":
    main()