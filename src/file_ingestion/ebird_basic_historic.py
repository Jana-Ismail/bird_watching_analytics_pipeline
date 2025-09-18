import io
import os
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as pv

from src.utils.logging_utils import setup_logger
from src.utils.date_utils import get_current_utc_timestamp
from src.utils.storage_utils import connect_to_minio, upload_parquet_to_minio
from src.config.app_settings import (
    LOG_FILE,
    MINIO_RAW_BUCKET_NAME,
    CA_REGION_CODE,
)

log_name = os.path.basename(__file__)
logger = setup_logger(log_name, LOG_FILE)

# Base prefix for historic files
RAW_HISTORIC_PREFIX = f"birds/observations/source=ebird/region={CA_REGION_CODE}/frequency=historic"

DOWNLOAD_DATE = get_current_utc_timestamp("%Y-%m-%d")


def convert_txt_to_parquet_arrow(raw_bytes, separator="\t", metadata=None):
    """
    Convert raw TXT/CSV bytes to a Parquet buffer using PyArrow directly.
    """
    read_options = pv.ReadOptions(use_threads=True, block_size=1 << 20)
    parse_options = pv.ParseOptions(delimiter=separator)
    convert_options = pv.ConvertOptions()

    table = pv.read_csv(
        io.BytesIO(raw_bytes),
        read_options=read_options,
        parse_options=parse_options,
        convert_options=convert_options,
    )

    if metadata:
        for col, value in metadata.items():
            table = table.append_column(col, pa.array([value] * table.num_rows))

    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression="zstd")
    buffer.seek(0)
    return buffer


def get_txt_files_from_minio(bucket_name=MINIO_RAW_BUCKET_NAME):
    """
    List only .txt files from MinIO under the raw historic txt prefix.
    """
    txt_prefix = f"{RAW_HISTORIC_PREFIX}/file_format=txt/"
    minio_client = connect_to_minio()
    objects = minio_client.list_objects(bucket_name, prefix=txt_prefix, recursive=True)
    return [obj.object_name for obj in objects if obj.object_name.endswith(".txt")]


def process_raw_file(object_name, timestamp, bucket_name=MINIO_RAW_BUCKET_NAME, separator="\t"):
    """
    Download a raw historic TXT file, convert to Parquet, and upload back
    to the parquet prefix under the same download_date.
    """
    minio_client = connect_to_minio()
    logger.info(f"Downloading {object_name} from {bucket_name}")

    # Download
    response = minio_client.get_object(bucket_name, object_name)
    raw_bytes = response.read()
    response.close()
    response.release_conn()

    # Metadata
    metadata = {
        "_source": "manual historic eBird .txt upload",
        "_source_object": object_name,
        "_ingested_at_utc": timestamp,
    }

    # Convert
    logger.info(f"Converting {object_name} to Parquet format with Arrow")
    parquet_buffer = convert_txt_to_parquet_arrow(raw_bytes, separator=separator, metadata=metadata)

    # Build new object path
    base_name = os.path.basename(object_name).rsplit(".", 1)[0] + ".parquet"
    parquet_object_name = (
        f"{RAW_HISTORIC_PREFIX}/file_format=parquet/download_date={DOWNLOAD_DATE}/{base_name}"
    )

    # Upload
    logger.info(f"Uploading Parquet file to {parquet_object_name}")
    upload_parquet_to_minio(
        parquet_buffer,
        object_name=parquet_object_name,
        bucket_name=bucket_name,
        logger=logger,
    )


def main():
    logger.info(f"Starting eBird historic ingestion from {RAW_HISTORIC_PREFIX}")
    timestamp = get_current_utc_timestamp("%Y-%m-%dT%H:%M:%S")

    files = get_txt_files_from_minio()
    if not files:
        logger.warning("No historic TXT files found to process")
        return

    for file in files:
        try:
            process_raw_file(file, timestamp)
        except Exception as e:
            logger.error(f"Failed to process {file}: {e}")


if __name__ == "__main__":
    main()
