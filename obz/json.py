# This file is placed in the Public Domain.
# pylint: disable=C,R,W0622


"a clean namespace"


import json as jsn


class Object:

    pass 


class Decoder(jsn.JSONDecoder):

    def __init__(self, *args, **kwargs):
        jsn.JSONDecoder.__init__(self, *args, **kwargs)

    def decode(self, s, _w=None):
        val = jsn.JSONDecoder.decode(self, s)
        if val is None:
            val = {}
        return val

    def raw_decode(self, s, idx=0):
        return jsn.JSONDecoder.raw_decode(self, s, idx)


def loads(string, *args, **kw):
    kw["cls"] = Decoder
    kw["object_hook"] = hook
    return jsn.loads(string, *args, **kw)


def hook(data):
    obj = Object()
    update(obj, data)
    return obj


def update(obj, data):
    if isinstance(data, type({})):
        obj.__dict__.update(data)
    else:
        obj.__dict__.update(vars(data))


class Encoder(jsn.JSONEncoder):

    def __init__(self, *args, **kwargs):
        jsn.JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        if isinstance(o, (type(str), type(True), type(False), type(int), type(float))):
            return o
        try:
            return jsn.JSONEncoder.default(self, o)
        except TypeError:
            try:
                return o.__dict__
            except AttributeError:
                return repr(o)

    def encode(self, o) -> str:
        return jsn.JSONEncoder.encode(self, o)

    def iterencode(self, o, _one_shot=False):
        return jsn.JSONEncoder.iterencode(self, o, _one_shot)


def dumps(*args, **kw):
    kw["cls"] = Encoder
    return jsn.dumps(*args, **kw)


def __dir__():
    return (
        'Decoder',
        'Encoder',
        'Object'
    )
