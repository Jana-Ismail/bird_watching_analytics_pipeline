from src.utils.logging_utils import setup_logger, get_log_name
from src.utils.storage_utils import create_duckdb_local_conn, create_duckdb_s3_conn, upload_file_to_minio, connect_to_minio, attach_ducklake_s3
from src.utils.file_utils import ensure_directory_exists
from src.config.app_settings import PROJECT_ROOT


def create_ducklake_catalog(conn):
    conn.execute(f"""
                    ATTACH 'ducklake:/Users/janaismail/workspace/de_2025/capstone/bird_sighting_analytics_pipeline/data/ducklake/bird_sightings.ducklake' 
                    AS bird_ducklake 
                    (DATA_PATH 's3://ducklake/catalog');"""
                 )
    conn.execute("USE bird_ducklake")
    create_ducklake_test_table(conn)

def create_ducklake_test_table(conn):
    conn.execute("CREATE SCHEMA IF NOT EXISTS test_schema")
    conn.execute("CREATE TABLE IF NOT EXISTS test_schema.test_table AS SELECT * FROM '/Users/janaismail/workspace/de_2025/capstone/bird_sighting_analytics_pipeline/data/test_data.csv'")

    
if __name__ == '__main__':
    logger = setup_logger(get_log_name(__file__), 'logs/setup_ducklake.log')

    duckdb_engine = ':memory:'
    s3_conn = create_duckdb_s3_conn(duckdb_engine)
    create_ducklake_catalog(s3_conn)

