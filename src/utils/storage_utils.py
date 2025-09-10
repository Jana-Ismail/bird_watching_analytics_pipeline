from minio import Minio
import duckdb

from src.config.app_settings import (
    MINIO_ACCESS_KEY,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY
)

def connect_to_minio():
    minio_client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    return minio_client

def upload_parquet_to_minio(data, object_name, logger, bucket_name):
    logger.info(f'Connecting to MinIO client')
    minio_client = connect_to_minio()
    if minio_client:
        logger.info(f'Connected to MinIO client')
    else:
        logger.error(f'Failed to connect to MinIO client')
        return

    try:
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            length=data.getbuffer().nbytes,
            content_type='application/parquet'
        )
        logger.info(f'Successfully uploaded {object_name} to MinIO')
    except Exception as e:
        logger.error(f'Error uploading to MinIO: {e}')
        raise

def connect_duckdb_to_minio(duckdb_db='bird_db.ducklake'):
    conn = duckdb.connect(duckdb_db)

    conn.execute('INSTALL httpfs;')
    conn.execute('INSTALL ducklake;')
    conn.execute('LOAD httpfs;')
    conn.execute('LOAD ducklake;')

    # Configure MinIO credentials
    conn.execute(f'SET s3_endpoint="{MINIO_ENDPOINT}"')
    conn.execute(f'SET s3_access_key_id="{MINIO_ACCESS_KEY}"')
    conn.execute(f'SET s3_secret_access_key="{MINIO_SECRET_KEY}"')
    conn.execute('SET s3_use_ssl=false')
    conn.execute('SET s3_region="us-east-1"')

    return conn

def create_ducklake(conn, duckdb_db=':memory:'):
    conn.execute(f"""
        ATTACH 'ducklake:{duckdb_db}' AS bird_ducklake
        (DATA_PATH '/Users/janaismail/workspace/de_2025/capstone/bird_sighting_analytics_pipeline/data/datalake/catalog');
    """)
        # (DATA_PATH 's3://ducklake/catalog');
    conn.execute('USE bird_ducklake;')

    # Medallion schemas
    for schema in ['bronze', 'silver', 'gold']:
        conn.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')