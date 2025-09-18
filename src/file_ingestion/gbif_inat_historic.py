import requests
import io
import os
import time
import zipfile

from src.utils.logging_utils import setup_logger
from src.utils.storage_utils import upload_parquet_to_minio
from src.utils.date_utils import get_current_utc_timestamp
from src.config.app_settings import (
    LOG_FILE,
    MINIO_RAW_BUCKET_NAME,
    CA_REGION_CODE,
)

log_name = os.path.basename(__file__)
logger = setup_logger(log_name, LOG_FILE)

GBIF_INAT_DATASET_KEY = "50c9509d-22c7-4a22-a47d-8c48425ef4a7"  # iNat
GBIF_AVES_TAXON_KEY = "212"
YEARS = [2025]

GBIF_USERNAME = os.getenv('GBIF_USERNAME')
GBIF_PASSWORD = os.getenv('GBIF_PASSWORD')
GBIF_EMAIL = os.getenv('GBIF_EMAIL')
GBIF_BASE_URL = 'https://api.gbif.org/v1/occurrence/download/request'
GBIF_DOWNLOAD_BASE_URL = 'https://api.gbif.org/v1/occurrence/download'

GBIF_REQUEST_JSON  = {
    'creator': GBIF_USERNAME,
    'notificationAddresses': [GBIF_EMAIL],
    'sendNotification': True,
    'format': 'SIMPLE_PARQUET',
    'predicate': {
        'type': 'and',
        'predicates': [
            {'type': 'equals', 'key': 'DATASET_KEY', 'value': GBIF_INAT_DATASET_KEY},
            {'type': 'equals', 'key': 'TAXON_KEY', 'value': GBIF_AVES_TAXON_KEY},
            {'type': 'equals', 'key': 'STATE_PROVINCE', 'value': 'California'},
            {'type': 'in', 'key': 'YEAR', 'values': YEARS},
        ]
    }
}

def get_gbif_inat_historic_parquet(base_url=GBIF_BASE_URL, request_json=GBIF_REQUEST_JSON, username=GBIF_USERNAME, password=GBIF_PASSWORD):
    try:
        response = requests.post(
            base_url,
            json=request_json,
            auth=(username, password),
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )

        response.raise_for_status()
        download_key = response.text.strip('"')
        
        return download_key
    except requests.exceptions.RequestException as e:
        logger.error(f"Error initiating GBIF download request: {e}")
        raise

def check_gbif_download_status(download_key):

    status_url = f'https://api.gbif.org/v1/occurrence/download/{download_key}'
    max_wait_minutes = 120   # stop after 2 hours
    poll_interval = 30       # seconds

    for _ in range(int(max_wait_minutes * 60 / poll_interval)):
        status = requests.get(status_url).json()
        logger.info(f'Download status: {status["status"]}')
        if status['status'] in ('SUCCEEDED', 'FAILED', 'CANCELLED'):
            break
        time.sleep(poll_interval)
    else:
        raise TimeoutError('Download did not finish within time limit.')

    return status

def download_gbif_zip(file_url):
    response = requests.get(file_url, stream=True)
    response.raise_for_status()

    file_bytes = io.BytesIO(response.content)
    return file_bytes

def main():
    timestamp = get_current_utc_timestamp("%Y-%m-%dT%H:%M:%S")
    download_date = timestamp.split('T')[0]
    download_key = get_gbif_inat_historic_parquet()

    status = check_gbif_download_status(download_key)

    if status['status'] != 'SUCCEEDED':
        raise RuntimeError(f'GBIF download failed with status: {status["status"]}')
    else:
        file_url = f'https://api.gbif.org/v1/occurrence/download/request/{download_key}'
        file_bytes = download_gbif_zip(file_url)
        year = YEARS[0]
        logger.info(f'Successfully downloaded GBIF iNat historic data for {year} for region {CA_REGION_CODE} from {file_url} at {timestamp}')

        with zipfile.ZipFile(file_bytes) as zip_file:
            for name in zip_file.namelist():
                if name.split('/')[0].endswith('.parquet'):
                    file_part = name.split('/')[-1]
                    file_name = f'gbif_inat_historic_{CA_REGION_CODE}_{year}_part-{file_part}.parquet'
                    object_name = f'birds/observations/source=inaturalist/region={CA_REGION_CODE}/frequency=historic/file_format=parquet/download_date={download_date}/{file_name}'
                    with zip_file.open(name) as parquet_file:
                        parquet_bytes = io.BytesIO(parquet_file.read())
                        upload_parquet_to_minio(
                            parquet_bytes, 
                            object_name=object_name, 
                            bucket_name=MINIO_RAW_BUCKET_NAME,
                            logger=logger
                        )
    

if __name__ == "__main__":
    main()

