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

def convert_data_to_parquet(data, metadata_columns=None):
    """
    Convert nested JSON/dict (or list of dicts) to a Parquet buffer using PyArrow.
    This preserves nested structs, lists, and maps.
    """
    if isinstance(data, dict):
        # Wrap in a list so Arrow sees it as one row
        data = [data]     
    elif isinstance(data, pd.DataFrame):
        data = data.to_dict(orient="records")

    table = pa.Table.from_pylist(data)
    num_rows = table.num_rows

    if metadata_columns:
        for col, value in metadata_columns.items():
            arr = pa.array([value] * num_rows)
            table = table.append_column(col, arr)

    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression="zstd")  # Other compression options: snappy, gzip
    buffer.seek(0)
    
    return buffer