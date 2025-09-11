from minio import Minio
import duckdb

from src.config.app_settings import (
    MINIO_ACCESS_KEY,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    MINIO_DUCKDB_S3_ENDPOINT
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
            content_type='application/octet-stream'
        )
        logger.info(f'Successfully uploaded {object_name} to MinIO')
    except Exception as e:
        logger.error(f'Error uploading to MinIO: {e}')
        raise

def upload_file_to_minio(file, object_name, logger, bucket_name):
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
            data=file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type='application/octet-stream'
        )
        logger.info(f'Successfully uploaded {object_name} to MinIO')
    except Exception as e:
        logger.error(f'Error uploading to MinIO: {e}')
        raise

def create_duckdb_s3_conn(duckdb_db):
    conn = duckdb.connect(duckdb_db)

    conn.execute("INSTALL httpfs;")
    conn.execute("INSTALL ducklake;")
    conn.execute("LOAD httpfs;")
    conn.execute("LOAD ducklake;")

    conn.execute(f"SET s3_endpoint='{MINIO_DUCKDB_S3_ENDPOINT}'")
    conn.execute(f"SET s3_access_key_id='{MINIO_ACCESS_KEY}'")
    conn.execute(f"SET s3_secret_access_key='{MINIO_SECRET_KEY}'")
    conn.execute("SET s3_use_ssl=false")
    conn.execute("SET s3_region='us-east-1'")
    conn.execute("SET s3_url_style='path'")

    return conn

def create_duckdb_local_conn(logger, duckdb_engine):
    logger.info(f'Creating local DuckDB connection with DuckDB database engine: {duckdb_engine}')
    conn = duckdb.connect(duckdb_engine)
    conn.execute("INSTALL ducklake;")
    conn.execute("LOAD ducklake;")

    return conn

def attach_ducklake(duckdb_engine):
    conn = create_duckdb_s3_conn(duckdb_engine)
    conn.execute(f"""
                    ATTACH 'ducklake:/Users/janaismail/workspace/de_2025/capstone/bird_sighting_analytics_pipeline/data/ducklake/bird_sightings.ducklake' 
                    AS bird_ducklake;
                """)
    conn.execute("USE bird_ducklake;")
    return conn
