def format_datetime(dt):
    if dt is not None:
        return dt.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
    return None
