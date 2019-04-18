from simplejson import dumps as _json_dumps


class Obj:

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def json_dumps(v, sort_keys=False):
    return _json_dumps(v, separators=(',', ':'), sort_keys=sort_keys)


assert json_dumps({'foo': 'bar'}) == '{"foo":"bar"}'
