from datetime import datetime


def timestamp_to_date(timestamp, view):
    if timestamp is None:
        return None
    if view == '%d.%m.%Y':
        normal_date = datetime.fromtimestamp(timestamp)
        return normal_date.strftime('%d.%m.%Y')
    elif view == '%Y-%m-%d':
        dt_object = datetime.utcfromtimestamp(timestamp)
        return dt_object.strftime('%Y-%m-%d')
    else:
        return None


def format_memory(memory_in_mb):
    gb = memory_in_mb / 1024
    if gb >= 1:
        return f"{int(gb)} Gb"
    else:
        return f"{int(memory_in_mb)} Mb"


def format_date(value, view='%d %b %Y'):
    try:
        date_obj = datetime.strptime(value, '%Y-%m-%d')
        formatted_date = date_obj.strftime(view)
        return formatted_date
    except ValueError:
        return value
