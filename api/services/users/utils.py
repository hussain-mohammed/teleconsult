from calendar import monthrange
from datetime import timedelta

from dateutil.parser import parse


def find_attribute(payload, attr_name):
    for user_attr in payload:
        if user_attr.get("Name") == attr_name:
            return user_attr.get("Value")
    return False


def get_month_date_range(date):
    data_obj = parse(date)
    year = data_obj.year
    month = data_obj.month

    # date range of the given month and year
    start, end = monthrange(year, month)
    start_date = (parse(f"{year}-{month}-1 12:00:01") - timedelta(1)).isoformat()
    end_date = (parse(f"{year}-{month}-{end} 23:59:59") + timedelta(1)).isoformat()
    return start_date, end_date
