# This file is placed in the Public Domain.
# pylint: disable=C,R,W0622


"a clean namespace"


import json


class Object:

    def __str__(self):
        return str(self.__dict__)


class Decoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, *args, **kwargs)

    def decode(self, s, _w=None):
        val = json.JSONDecoder.decode(self, s)
        if val is None:
            val = {}
        return val

    def raw_decode(self, s, idx=0):
        return json.JSONDecoder.raw_decode(self, s, idx)


class Encoder(json.JSONEncoder):

    def __init__(self, *args, **kwargs):
        json.JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o):
        try:
            return o.items()
        except AttributeError:
            pass
        try:
            return vars(o)
        except ValueError:
            pass
        try:
            return iter(o)
        except ValueError:
            pass
        return json.JSONEncoder.default(self, o)

    def encode(self, o) -> str:
        return json.JSONEncoder.encode(self, o)

    def iterencode(self, o, _one_shot=False):
        return json.JSONEncoder.iterencode(self, o, _one_shot)


"json"


def dumps(*args, **kw):
    kw["cls"] = Encoder
    return json.dumps(*args, **kw)


def hook(data):
    obj = Object()
    construct(obj, data)
    return obj


def loads(string, *args, **kw):
    kw["cls"] = Decoder
    kw["object_hook"] = hook
    return json.loads(string, *args, **kw)


"methods"


def construct(obj, *args, **kwargs):
    if args:
        val = args[0]
        try:
            update(obj, vars(val))
        except TypeError:
            try:
                update(obj, val)
            except ValueError:
                update(obj, dict(val))
    if kwargs:
        update(obj, kwargs)


def items(obj):
    if isinstance(obj,type({})):
        return obj.items()
    return obj.__dict__.items()


def keys(obj):
    if isinstance(obj, type({})):
        return obj.keys()
    return list(obj.__dict__.keys())


def update(obj, data):
    if isinstance(data, type({})):
        obj.__dict__.update(data)
    else:
        obj.__dict__.update(vars(data))


def values(obj):
    return obj.__dict__.values()


"interface"


def __dir__():
    return (
        'Decoder',
        'Encoder',
        'Object',
        'construct',
        'keys',
        'items',
        'values',
        'update'
    )
