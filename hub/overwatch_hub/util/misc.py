import reprlib


_repr_obj = reprlib.Repr()
_repr_obj.maxstr = 60
_repr_obj.maxother = 60

smart_repr = _repr_obj.repr
