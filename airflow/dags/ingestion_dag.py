import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

DEV_CONTAINER_ROOT = '/opt/airflow'
if DEV_CONTAINER_ROOT not in sys.path:
    sys.path.append(DEV_CONTAINER_ROOT)

try:
    from src.api_ingestion.ebird_daily import main as ebird_main
    from src.api_ingestion.inaturalist_daily import main as inat_main
    from src.api_ingestion.nasa_firms_fire_daily import main as nasa_firms_main
    from src.api_ingestion.open_meteo_daily import main as open_meteo_main
except ImportError as e:
    logger.error(f'ERROR: Could not import external scripts. Check Airflow PYTHONPATH in Airflow containers.')
    logger.error(f'ImportError: {e}')
    raise