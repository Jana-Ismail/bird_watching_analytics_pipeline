from minio import Minio

from src.config.app_settings import (
    MINIO_ACCESS_KEY,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    MINIO_BUCKET_NAME
)


def connect_to_minio():
    minio_client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    return minio_client

def upload_parquet_to_minio(data, object_name, logger, bucket_name=MINIO_BUCKET_NAME):
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