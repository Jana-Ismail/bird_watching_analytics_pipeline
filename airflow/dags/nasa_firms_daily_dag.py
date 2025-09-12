import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

DEV_CONTAINER_ROOT = '/opt/airflow'
if DEV_CONTAINER_ROOT not in sys.path:
    sys.path.append(DEV_CONTAINER_ROOT)

from src.utils.logging_utils import setup_logger, get_log_name

logger = setup_logger(get_log_name(__file__), '/opt/airflow/logs/ingestion_dag.log')

try:
    from src.api_ingestion.weather.nasa_firms_fire_daily import main as nasa_firms_daily_main
except ImportError as e:
    logger.error(f'ERROR: Could not import external scripts. Check Airflow PYTHONPATH in Airflow containers.')
    logger.error(f'ImportError: {e}')
    raise

def run_nasa_firms_ingestion(**kwargs):
    kwargs['ti'].log.info(f'Running ebird_daily_main for DAG run {kwargs["dag_run"].run_id}')
    nasa_firms_daily_main()
    kwargs['ti'].log.info(f'Completed ebird_daily_main for DAG run {kwargs["dag_run"].run_id}')

with DAG(
    dag_id='nasa_firms_daily_weather_ingestion_pipeline',
    start_date=days_ago(1),
    schedule_interval='0 17 * * *',
    catchup=False,
    tags=['weather', 'fire', 'daily_ingestion', 'nasa_firms', 'api', 'raw', 'minio']
) as dag:

    nasa_firms_daily_api_to_minio_task = PythonOperator(
        task_id='run_open_meteo_daily_ingestion',
        python_callable=run_nasa_firms_ingestion,
        provide_context=True
    )
