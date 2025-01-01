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
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        if isinstance(o, (type(str), type(True), type(False), type(int), type(float))):
            return o
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            try:
                return o.__dict__
            except AttributeError:
                return repr(o)

    def encode(self, o) -> str:
        return json.JSONEncoder.encode(self, o)

    def iterencode(self, o, _one_shot=False):
        return json.JSONEncoder.iterencode(self, o, _one_shot)


def dumps(*args, **kw):
    kw["cls"] = Encoder
    return json.dumps(*args, **kw)


def hook(data):
    obj = Object()
    obj.__dict__.update(data)
    return obj


def loads(string, *args, **kw):
    kw["cls"] = Decoder
    kw["object_hook"] = hook
    return json.loads(string, *args, **kw)


def __dir__():
    return (
        'Decoder',
        'Encoder',
        'Object'
    )
