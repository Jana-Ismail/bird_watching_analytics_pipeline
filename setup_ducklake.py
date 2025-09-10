from src.utils.logging_utils import setup_logger, get_log_name
from src.utils.storage_utils import connect_duckdb_to_minio, create_ducklake

logger = setup_logger(get_log_name(__file__), 'logs/setup_ducklake.log')

def create_ducklake_warehouse(conn, duckdb_db='bird_db.ducklake'):
    conn.execute(f"""
        ATTACH 'ducklake:{duckdb_db}' AS bird_ducklake
        (DATA_PATH '/Users/janaismail/workspace/de_2025/capstone/bird_sighting_analytics_pipeline/data/catalog')
    """)
        # (DATA_PATH 's3://ducklake/catalog');
    conn.execute('USE bird_ducklake;')

    # Medallion schemas
    conn.execute(f'CREATE SCHEMA IF NOT EXISTS bronze')
    conn.execute(f'CREATE SCHEMA IF NOT EXISTS silver')
    conn.execute(f'CREATE SCHEMA IF NOT EXISTS gold')

    tables = conn.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        ORDER BY table_schema, table_name
    """).fetchall()
    
    for schema, table in tables:
        logger.info(f'Table: {schema}.{table}')

    
if __name__ == '__main__':
    duckdb_db = ':memory:'
    conn = connect_duckdb_to_minio(duckdb_db)
    create_ducklake(conn)