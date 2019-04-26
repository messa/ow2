import reprlib
from secrets import token_urlsafe
from simplejson import dumps as json_dumps


_repr_obj = reprlib.Repr()
_repr_obj.maxstr = 60
_repr_obj.maxother = 60

smart_repr = _repr_obj.repr


def random_str(length):
    while True:
        x = token_urlsafe(length)
        x = x[:length]
        if not x.isalnum():
            continue
        return x.lower()


def to_compact_json(obj):
    return json_dumps(obj, separators=(',', ':'))
