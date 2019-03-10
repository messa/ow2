from datetime import datetime
import pytz
import reprlib
from secrets import token_urlsafe
from simplejson import dumps as json_dumps


_repr_obj = reprlib.Repr()
_repr_obj.maxstr = 60
_repr_obj.maxother = 60

smart_repr = _repr_obj.repr


def parse_datetime(dt_str):
    if not isinstance(dt_str, str):
        raise Exception(f'Expected str: {dt_str!r}')
    try:
        if dt_str.endswith('Z'):
            dt_str = dt_str[:-1] + '+00:00'
        dt = datetime.fromisoformat(dt_str)
        dt = pytz.utc.normalize(dt) if dt.tzinfo else pytz.utc.localize(dt)
        return dt
    except Exception as e:
        raise Exception(f'Failed to parse datetime {dt_str!r}: {e!r}')


def random_str(length):
    while True:
        x = token_urlsafe(length)
        x = x[:length]
        if not x.isalnum():
            continue
        return x


def to_compact_json(obj):
    return json_dumps(obj, separators=(',', ':'))
