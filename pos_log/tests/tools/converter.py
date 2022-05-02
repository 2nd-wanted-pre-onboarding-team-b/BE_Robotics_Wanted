from datetime import datetime

TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
def str2datetime(s: str) -> datetime:
    # string -> datetime
    if not s:
        return None
    return datetime.strptime(s, TIME_FORMAT)

