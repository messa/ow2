from datetime import datetime
from pytz import utc


def to_utc(dt):
    try:
        return utc.normalize(dt) if dt.tzinfo else utc.localize(dt)
    except Exception as e:
        raise Exception(f'Failed to convert {dt!r} to UTC: {e!r}')


def parse_datetime(dt_str):
    if not isinstance(dt_str, str):
        raise Exception(f'Expected str: {dt_str!r}')
    try:
        if dt_str.endswith('Z'):
            dt_str = dt_str[:-1] + '+00:00'
        dt = datetime.fromisoformat(dt_str)
        dt = to_utc(dt)
        return dt
    except Exception as e:
        raise Exception(f'Failed to parse datetime {dt_str!r}: {e!r}')
