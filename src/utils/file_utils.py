from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import io
from io import BytesIO

def ensure_directory_exists(path):
    """Create directory if it doesn't exist"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    
    return path

def convert_json_to_parquet(data):
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    buffer = BytesIO()
    data.to_parquet(buffer, index=False)
    buffer.seek(0)
    
    return buffer

def convert_nested_json_to_parquet(data):
    """
    Convert nested JSON/dict (or list of dicts) to a Parquet buffer using PyArrow.
    This preserves nested structs, lists, and maps.
    """
    if isinstance(data, dict):
        # Wrap in a list so Arrow sees it as one row
        data = [data]

    table = pa.Table.from_pylist(data)
    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression="zstd")  # or snappy, gzip, etc.
    buffer.seek(0)
    return buffer