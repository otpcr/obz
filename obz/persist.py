# This file is placed in the Public Domain.
# pylint: disable=C,R0903,W0105,W0622,W0719,E1101


"persistence"


import datetime
import json
import os
import pathlib
import time
import _thread


from .object import Object, dumps, items, keys, loads, update


cachelock = _thread.allocate_lock()
disklock  = _thread.allocate_lock()
findlock  = _thread.allocate_lock()
lock      = _thread.allocate_lock()
p         = os.path.join


class Config:

    fqns = []
    wdr  = ""

    def __getattr__(self, key):
        return self.__dict__.get(key, "")


class Cache:

    objs = {}

    @staticmethod
    def add(path, obj):
        with cachelock:
            Cache.objs[path] = obj

    @staticmethod
    def get(path):
        with cachelock:
            return Cache.objs.get(path)

    @staticmethod
    def typed(matcher):
        with cachelock:
            for key in Cache.objs:
                if matcher not in key:
                    continue
                yield Cache.objs.get(key)


"path"


def cdir(pth):
    path = pathlib.Path(pth)
    path.parent.mkdir(parents=True, exist_ok=True)


def long(name):
    split = name.split(".")[-1].lower()
    res = name
    for names in types():
        if split == names.split(".")[-1].lower():
            res = names
            break
    return res


def modname():
    return p(Config.wdr, "mods")


def pidname(name):
    return p(Config.wdr, f"{name}.pid")


def skel():
    stor = p(Config.wdr, "store", "")
    path = pathlib.Path(stor)
    path.mkdir(parents=True, exist_ok=True)
    return path


def store(pth=""):
    stor = p(Config.wdr, "store", "")
    if not os.path.exists(stor):
        skel()
    return p(Config.wdr, "store", pth)


def types():
    return os.listdir(store())


"utilities"




def pidfile(filename):
    if os.path.exists(filename):
        os.unlink(filename)
    path2 = pathlib.Path(filename)
    path2.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fds:
        fds.write(str(os.getpid()))




def strip(pth, nmr=3):
    return os.sep.join(pth.split(os.sep)[-nmr:])


"methods"


def fetch(obj, pth):
    with lock:
        with open(pth, 'r', encoding='utf-8') as ofile:
            try:
                obj2 = loads(ofile.read())
                update(obj, obj2)
            except json.decoder.JSONDecodeError as ex:
                raise Exception(pth) from ex


def format(obj, args=None, skip=None, plain=False):
    if args is None:
        args = keys(obj)
    if skip is None:
        skip = []
    txt = ""
    for key in args:
        if key.startswith("__"):
            continue
        if key in skip:
            continue
        value = getattr(obj, key, None)
        if value is None:
            continue
        if plain:
            txt += f"{value} "
        elif isinstance(value, str) and len(value.split()) >= 2:
            txt += f'{key}="{value}" '
        else:
            txt += f'{key}={value} '
    return txt.strip()


def fqn(obj):
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = f"{obj.__module__}.{obj.__name__}"
    return kin


def ident(obj):
    return p(fqn(obj), *str(datetime.datetime.now()).split())


def read(obj, pth):
    with disklock:
        pth2 = store(pth)
        fetch(obj, pth2)
        return os.sep.join(pth.split(os.sep)[-3:])


def sync(obj, pth):
    with lock:
        cdir(pth)
        txt = dumps(obj, indent=4)
        with open(pth, 'w', encoding='utf-8') as ofile:
            ofile.write(txt)


def write(obj, pth=None):
    if pth is None:
        pth = ident(obj)
    with disklock:
        pth2 = store(pth)
        sync(obj, pth2)
        return pth


"interface"


def __dir__():
    return (
        'Config',
        'edit',
        'find',
        'format',
        'last',
        'match',
        'read',
        'search',
        'write'
    )
