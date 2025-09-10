from src.utils.logging_utils import setup_logger, get_log_name
from src.utils.storage_utils import create_duckdb_local_conn
from src.utils.file_utils import ensure_directory_exists
from src.config.app_settings import PROJECT_ROOT


def create_ducklake_instance(conn, ducklake_db, duckdb_engine=':memory:'):
    ducklake_dir = ensure_directory_exists( PROJECT_ROOT / 'data' / 'ducklake')
    ducklake_catalog_dir = ensure_directory_exists(ducklake_dir / 'catalog')
    ducklake_metadata_path = ducklake_dir / ducklake_db
    logger.info(f'DuckLake catalog path: {ducklake_catalog_dir}')

    
    conn.execute(f"ATTACH 'ducklake:{ducklake_metadata_path}' AS bird_ducklake (DATA_PATH '{ducklake_catalog_dir}')")
        # (DATA_PATH 's3://ducklake/catalog');
    conn.execute("USE bird_ducklake;")

    # Medallion schemas
    conn.execute(f'CREATE SCHEMA IF NOT EXISTS bronze')
    conn.execute(f'CREATE SCHEMA IF NOT EXISTS silver')
    conn.execute(f'CREATE SCHEMA IF NOT EXISTS gold')

    schemas = conn.execute("SELECT schema_name FROM information_schema.schemata WHERE catalog_name = 'bird_ducklake'").fetchall()
    
    for schema in schemas:
        logger.info(f'Schema: {schema}')
    
    create_ducklake_test_table(conn)

def create_ducklake_test_table(conn):
    conn.execute("CREATE SCHEMA IF NOT EXISTS test_schema")
    conn.execute("CREATE TABLE IF NOT EXISTS test_schema.test_table AS SELECT * FROM '/Users/janaismail/workspace/de_2025/capstone/bird_sighting_analytics_pipeline/data/test_data.csv'")

    
if __name__ == '__main__':
    logger = setup_logger(get_log_name(__file__), 'logs/setup_ducklake.log')

    duckdb_engine = ':memory:'
    ducklake_metadata_file = 'bird_sightings.ducklake'

    conn = create_duckdb_local_conn(logger)

    logger.info(f'Using instance of DuckDB {duckdb_engine} database as analytical engine.')
    logger.info(f'Creating DuckLake instance: {ducklake_metadata_file}')
    create_ducklake_instance(conn, ducklake_metadata_file, duckdb_engine)

    conn.close()

