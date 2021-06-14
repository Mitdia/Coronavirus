from datetime import datetime


def check_date_format(date_string):
    format = "%Y-%m-%d"
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False
