import os
import requests
import math

from src.utils.logging_utils import setup_logger
from src.utils.date_utils import get_current_utc_timestamp, get_pacific_target_date
from src.utils.storage_utils import upload_parquet_to_minio
from src.utils.file_utils import convert_data_to_parquet
from src.config.app_settings import (
    LOG_FILE,
    MINIO_RAW_BUCKET_NAME,
    CA_REGION_CODE,
)

log_name = os.path.basename(__file__)
logger = setup_logger(log_name, LOG_FILE)

INAT_BASE_URL = "https://api.inaturalist.org/v1/observations"

CA_INAT_HOTSPOTS = [
    {
        'place_name': 'monterey_bay',
        'place_id': 118063,
    },
    {
        'place_name': 'san_francisco_valley',
        'place_id': 54321,
    },
    {
        'place_name': 'san_joaquin_valley',
        'place_id': 157602,
    },
    {
        'place_name': 'sacramento_valley',
        'place_id': 157601,
    },
    {}

]

def get_inaturalist_observations(start_date, end_date, place_id, per_page=200):
    """
    Fetch all iNaturalist observations for a given place_id and date range.
    Pagination is handled explicitly (no while True).
    """
    params = {
        "quality_grade": "any",
        "identifications": "any",
        "iconic_taxa[]": "Aves",
        "place_id": place_id,
        "d1": start_date,
        "d2": end_date,
        "per_page": per_page,
        "page": 1,
    }

    logger.info(f"Fetching iNaturalist observations for place_id={place_id}, "
                f"date range {start_date} to {end_date}")

    try:
        response = requests.get(INAT_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from iNaturalist API: {e}")
        raise

    first_page = response.json()
    total_results = first_page.get("total_results", 0)
    results = first_page.get("results", [])

    if total_results == 0:
        logger.warning("No results found")
        return [], response.url, total_results

    if total_results > 10000:
        logger.warning("Total results exceed iNaturalist API limit of 10,000 requests per day")
        return [], response.url, total_results

    total_pages = math.ceil(total_results / per_page)
    logger.info(f"Total results: {total_results}, total pages: {total_pages}")

    # Fetch remaining pages
    for page in range(2, total_pages + 1):
        params["page"] = page
        try:
            response = requests.get(INAT_BASE_URL, params=params, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page {page} from iNaturalist API: {e}")
            raise

        page_data = response.json().get("results", [])
        results.extend(page_data)

    return results, response.url, total_results


def process_inat_data(data, place_id, place_name, year, start_date, end_date, timestamp, url, total_results):
    logger.info("Converting iNaturalist API data to Parquet format")

    metadata = {
        "_source": "iNaturalist API",
        "_source_url": url,
        "_ingested_at_utc": timestamp,
        "_total_results": total_results,
    }

    observations_buffer = convert_data_to_parquet(data, metadata)

    logger.info("Uploading Parquet file to MinIO")
    file_name = f"inat_obs_{place_name}_{start_date}.parquet"
    object_name = (f"birds/observations/source=inaturalist/"
                   f"region={CA_REGION_CODE}/hotspot={place_name}/frequency=yearly/date={year}/{file_name}")
    upload_parquet_to_minio(observations_buffer,
                            object_name=object_name,
                            bucket_name=MINIO_RAW_BUCKET_NAME,
                            logger=logger)

def clean_inat_records(records):
    """Recursively clean empty dicts/lists that Arrow cannot handle."""
    def clean_value(v):
        if isinstance(v, dict):
            if not v:  # empty dict
                return None
            return {k: clean_value(val) for k, val in v.items()}
        elif isinstance(v, list):
            if not v:  # empty list
                return None
            return [clean_value(i) for i in v]
        else:
            return v

    return [clean_value(r) for r in records]


def main():
    timestamp = get_current_utc_timestamp("%Y-%m-%dT%H:%M:%S")

    # Example: dynamically fetch "yesterday in Pacific"
    # days_ago = 2
    # start_date = get_pacific_target_date("%Y-%m-%d", days_ago)
    # end_date = get_pacific_target_date("%Y-%m-%dT23:59:59", days_ago)
    years = [2023, 2024]
    for year in years:
        start_date = f'{year}-07-01'
        end_date = f'{year}-12-31'

        # place_id = 118063  # example CA hotspot
        # place_name = "monterey_bay"

        # place_id = 54321
        # place_name = 'san_francisco_valley'

        try:
            observations, url, total_results = get_inaturalist_observations(start_date, end_date, place_id)
        except Exception as e:
            logger.error(f"Failed to fetch iNaturalist data: {e}")
            raise

        if not observations:
            logger.warning(f"No observations found for place_id={place_id}")
            return
        else:
            observations = clean_inat_records(observations)
            process_inat_data(observations, place_id, place_name, year, start_date, end_date, timestamp, url, total_results)


if __name__ == "__main__":
    main()
