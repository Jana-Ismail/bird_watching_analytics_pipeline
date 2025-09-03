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
EBIRD_OBSERVATION_BASE_URL = os.getenv('EBIRD_OBSERVATION_BASE_URL')

EBIRD_REGION_CODE = 'US-CO'
EBIRD_OBSERVATION_ENDPOINTS = {
    "recent_by_region": f"{EBIRD_OBSERVATION_BASE_URL}/data/obs/{EBIRD_REGION_CODE}/recent",
}