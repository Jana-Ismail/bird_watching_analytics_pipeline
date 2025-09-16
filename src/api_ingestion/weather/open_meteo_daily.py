import json, time, requests
import pandas as pd
import sys

from src.config.app_settings import (
    LOG_FILE,
    PROJECT_ROOT,
    OPEN_METEO_BASE_URL,
    PACIFIC_TIMEZONE,
    CA_REGION_CODE,
    METEO_TILES_40KM_FILE_PATH as METEO_TILES_PATH,
    METEO_DAILY_PARAMS,
)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.utils.logging_utils import setup_logger, get_log_name
from src.utils.file_utils import convert_data_to_parquet
from src.utils.date_utils import get_current_utc_timestamp, get_pacific_target_date
from src.utils.storage_utils import upload_parquet_to_minio

logger = setup_logger(get_log_name(__file__), LOG_FILE)

def fetch_open_meteo_weather_daily(
        url,
        latitude, 
        longitude, 
        start_date,
        end_date,
        timezone=PACIFIC_TIMEZONE,
        max_retries=5,
        timeout=60
    ):
    """
    Returns dict with 'latitude', 'longitude', 'timezone', 'elevation', 'daily_units', and 'daily' dict for the requested variables and 'time' as array values.
    Dates are inclusive. Units in 'daily_units'.
    """
    daily_params = METEO_DAILY_PARAMS
    # Optional 'daily' params str: 'temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,winddirection_10m_dominant',
    query_params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start_date,
        'end_date': end_date,
        'timezone': timezone,
        'daily': daily_params
    }
    
    backoff = 1.0

    try:
        for _ in range(max_retries):
            response = requests.get(url, params=query_params, timeout=timeout)

            # Response status code 429 indicates too many requests
            if response.status_code == 429:
                time.sleep(backoff)
                backoff *= 1.8
                continue

        response.raise_for_status()
        weather = response.json()
        request_url = response.url

        return weather, request_url

    except RuntimeError as e:
        logger.error(f'Open Meteo: exceed retries. Error: {e}')
        raise
    except Exception as e:
        logger.error(f'Error parsing JSON response: {e}')
        raise


def fetch_open_meteo_coordinate_tiles(url, tiles_file_path, target_date, timestamp_utc):
    """Fetch Open Meteo weather data for a list of coordinate tiles and a specific date."""
    logger.info(f'Fetching Open Meteo weather data for grid of tiles from file: {tiles_file_path} on date: {target_date}')
    
    start_date = target_date
    end_date = start_date  # Open Meteo uses inclusive dates

    logger.info(f'Getting grid tile coordinates from {tiles_file_path}')
    with open(tiles_file_path) as file:
        tiles = json.load(file)

    logger.info(f'Ingesting weather data for {len(tiles)} tiles for date: {target_date}')
    for tile in tiles:
        tile_id = tile['id']
        latitude = tile['lat']
        longitude =  tile['lon']

        try:
            logger.info(f'Fetching weather data for tile {tile_id} at ({latitude}, {longitude}) for date {target_date} at ingestion_time {timestamp_utc}')
            weather, request_url = fetch_open_meteo_weather_daily(url, latitude, longitude, start_date, end_date)
            logger.info(f'Fetched weather for tile {tile_id} at ({latitude}, {longitude}) for date {target_date} at ingestion_time {timestamp_utc}')
        except Exception as e:
            logger.error(f'Error fetching weather for tile {tile_id} at ({latitude}, {longitude}) for date {target_date} at ingestion_time {timestamp_utc}: {e}')
            continue

        if not weather:
            logger.info(f'No weather data found for tile {tile_id} at ({latitude}, {longitude}) for date {target_date} at ingestion_time {timestamp_utc}')
            continue
        else:
            process_tile_weather_data(weather, request_url, tile_id, latitude, longitude, target_date, timestamp_utc)

        time.sleep(0.2)

def process_tile_weather_data(data, request_url, tile_id, latitude, longitude, target_date, timestamp_utc):
        logger.info(f'Converting weather data to Parquet for tile {tile_id} at ({latitude}, {longitude}) for date {target_date} at ingestion_time {timestamp_utc}')
        
        metadata = {
            '_source': 'Open-Meteo API',
            '_source_url': request_url,
            '_ingested_at_utc': timestamp_utc,
        }

        weather_buffer = convert_data_to_parquet(data, metadata_columns=metadata)

        logger.info(f'Uploading weather data to MinIO for tile {tile_id} at ({latitude}, {longitude}) for date {target_date} at ingestion_time {timestamp_utc}')
        file_name = f'open-meteo_weather_{CA_REGION_CODE}_{target_date}_tile-{tile_id}.parquet'
        object_name = f'weather/general/source=open-meteo/region={CA_REGION_CODE}/frequency=daily/date={target_date}/grid_size=40km/tile={tile_id}/{file_name}'
        upload_parquet_to_minio(weather_buffer, object_name=object_name, bucket_name='raw', logger=logger)
        logger.info(f'Successfully uploaded weather data to MinIO for tile {tile_id} at ({latitude}, {longitude}) for date {target_date} at ingestion_time {timestamp_utc}')

def main():
    url = OPEN_METEO_BASE_URL
    tiles_file_path = METEO_TILES_PATH
    target_date = get_pacific_target_date('%Y-%m-%d', days_ago=3)
    timestamp = get_current_utc_timestamp('%Y-%m-%dT%H:%M:%S')

    fetch_open_meteo_coordinate_tiles(url, tiles_file_path, target_date, timestamp)

if __name__ == '__main__':
    main()