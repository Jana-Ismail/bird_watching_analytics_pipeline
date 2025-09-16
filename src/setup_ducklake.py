from src.utils.logging_utils import setup_logger, get_log_name
from src.utils.storage_utils import create_duckdb_s3_conn, attach_ducklake
from src.utils.file_utils import ensure_directory_exists
from src.config.app_settings import PROJECT_ROOT

logger = setup_logger(get_log_name(__file__), 'logs/setup_ducklake.log')

def create_ducklake_catalog(conn):
    ensure_directory_exists(PROJECT_ROOT / 'data' / 'ducklake')
    conn.execute(f"""
                    ATTACH 'ducklake:/Users/janaismail/workspace/de_2025/capstone/bird_sighting_analytics_pipeline/data/ducklake/bird_sightings.ducklake' 
                    AS bird_ducklake 
                    (DATA_PATH 's3://ducklake/catalog');"""
                 )
    conn.execute("USE bird_ducklake")
    # create_ducklake_test_table(conn)


def create_ducklake_test_table(conn):
    conn.execute("CREATE SCHEMA IF NOT EXISTS test_schema")
    conn.execute("CREATE TABLE IF NOT EXISTS test_schema.test_table AS SELECT * FROM '/Users/janaismail/workspace/de_2025/capstone/bird_sighting_analytics_pipeline/data/test_data.csv'")

def create_ducklake_schemas(conn):
    logger.info("Creating 'bronze', 'silver', and 'gold' schemas in DuckLake catalog.")
    conn.execute("CREATE SCHEMA IF NOT EXISTS bronze")
    conn.execute("CREATE SCHEMA IF NOT EXISTS silver")
    conn.execute("CREATE SCHEMA IF NOT EXISTS gold")

def validate_ducklake_schemas(conn):
    logger.info("Validating successful creation of 'bronze', 'silver', and 'gold' schemas in DuckLake catalog.")
    
    for schema in ['bronze', 'silver', 'gold']:
        try:
            found_schema = conn.execute(f"""
                SELECT 1 
                FROM INFORMATION_SCHEMA.SCHEMATA 
                WHERE catalog_name='bird_ducklake' 
                    AND schema_name='{schema}';"""
            ).fetchone()

            if found_schema:
                logger.info(f"Schema '{schema}' successfully created.")
            else:
                logger.error(f"Schema '{schema}' not found.")
                return False
        except Exception as e:
            logger.error(f"Error validating schema '{schema}': {e}")
            return False
        
    return True
    
def list_ducklake_schemas(conn):
    
    schemas = conn.execute("""
        SELECT schema_name
        FROM information_schema.schemata 
        WHERE catalog_name='bird_ducklake';"""
    ).fetchdf()

    print(schemas)

def list_ducklake_tables(conn):
    tables = conn.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_catalog = 'bird_ducklake'
            AND table_schema IN ('bronze', 'silver', 'gold');"""
    ).fetchdf()

    print(tables)

def main():
    duckdb_engine = ':memory:'
    s3_conn = create_duckdb_s3_conn(duckdb_engine)
    create_ducklake_catalog(s3_conn)
    s3_conn.close()

    s3_conn = attach_ducklake(duckdb_engine)
    create_ducklake_schemas(s3_conn)

    # list_ducklake_schemas(s3_conn)
    list_ducklake_tables(s3_conn)

    # valid_schemas = validate_ducklake_schemas(s3_conn)
    # if valid_schemas:
    #     logger.info("DuckLake setup completed successfully.")
    # else:
    #     logger.error("DuckLake setup encountered issues.")

    s3_conn.close()

if __name__ == '__main__':
    main()
