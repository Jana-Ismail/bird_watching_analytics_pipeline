import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Logging Credentials
LOG_DIR = PROJECT_ROOT / 'logs'
LOG_FILE = LOG_DIR / 'bird_watching_analytics_pipeline.log'

# Ebird API Credentials
EBIRD_API_KEY = os.getenv('EBIRD_API_KEY')
EBIRD_BASE_URL = os.getenv('EBIRD_BASE_URL')

EBIRD_REGION_CODE = 'US-CA'

EBIRD_ENDPOINTS = {
    'taxonomy': '/ref/taxonomy/ebird',
    'regional_hotspots': '/ref/hotspot/{{regionCode}}',
    'hotspot_information': '/ref/hotspot/info/{{locId}}',
    'region_info': '/ref/region/info/{{regionCode}}'
}

# Minio Credentials
MINIO_ENDPOINT = os.getenv('MINIO_URL_HOST_PORT')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')