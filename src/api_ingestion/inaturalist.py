from io import BytesIO
import os
import pandas as pd
from datetime import datetime
from pyinaturalist import get_observations

from src.utils.logging_utils import setup_logger
from src.utils.date_utils import get_current_utc_timestamp
from src.utils.storage_utils import connect_to_minio
from src.config.app_settings import (
    LOG_FILE,
    MINIO_BUCKET_NAME,
    CA_BIRD_HOTSPOTS,
    BIRDS_TAXON_NAME
)

log_name = os.path.basename(__file__)
logger = setup_logger(log_name, LOG_FILE)

def get_inaturalist_observations_by_location(
        hotspot_name, latitude, longitude, radius_km, 
        start_date, end_date, per_page=200):
    """GET bird observations from iNaturalist API for a specific location and date range."""

    logger.info(f'Fetching bird observations from iNaturalist API for hotspot: {hotspot_name} at location ({latitude}, {longitude}) within radius {radius_km} km '
                f'from {start_date} to {end_date}')

    try:
        observations = get_observations(
            taxon_name=BIRDS_TAXON_NAME,
            latitude=latitude,
            longitude=longitude,
            radius=radius_km,
            d1=start_date,
            d2=end_date,
            per_page=per_page,
            only_id=False, # Get full observation details or not
            geo=False,  # Include geo tagged data or not - including for raw, will filter later
            verifiable=False, # Include research-grade observations or not
            order_by='observed_on',
            order='desc',
            sounds=False, # Exclude sounds-only observations,
            captive=False   # Exclude zoo/captive observations
        )
    except Exception as e:
        logger.error(f'Error fetching observations from iNaturalist API: {e}')
        raise

    return observations.get('results', [])

def main():
    hotspot_name = 'point_reyes'
    hotspot_data = CA_BIRD_HOTSPOTS[hotspot_name] 
    latitude = hotspot_data['latitude']
    longitude = hotspot_data['longitude']
    radius_km = hotspot_data['radius_km']
    start_date = '2025-08-01'
    end_date = '2025-09-02'

    observations = get_inaturalist_observations_by_location(
        hotspot_name,
        latitude,
        longitude,
        radius_km,
        start_date,
        end_date
    )

    # Process observations as needed
    print(observations)

if __name__ == "__main__":
    main()