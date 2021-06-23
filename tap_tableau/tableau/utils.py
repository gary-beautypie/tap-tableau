def format_datetime(dt):
    return dt.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
