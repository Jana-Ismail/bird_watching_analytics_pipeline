from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

def get_current_utc_timestamp(date_format_str):
    return datetime.now(timezone.utc).strftime(date_format_str)

def get_pacific_day_range_for_inat():
    timezone = ZoneInfo('America/Los_Angeles')
    today_pacific = datetime.now(timezone).date()
    yesterday_pacific = today_pacific - timedelta(days=1)
    start_date = yesterday_pacific.strftime('%Y-%m-%d')
    end_date = yesterday_pacific.strftime('%Y-%m-%dT23:59:59')

    return start_date, end_date
