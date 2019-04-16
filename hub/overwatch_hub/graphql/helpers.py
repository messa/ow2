from simplejson import dumps as _json_dumps


class Obj:

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def json_dumps(v):
    return _json_dumps(v, separators=(',', ':'))


assert json_dumps({'foo': 'bar'}) == '{"foo":"bar"}'
