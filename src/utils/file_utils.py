from pathlib import Path
import pandas as pd
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