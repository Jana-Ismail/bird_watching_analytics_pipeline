from datetime import datetime, timezone

def get_current_utc_timestamp(date_format_str):
    return datetime.now(timezone.utc).strftime(date_format_str)