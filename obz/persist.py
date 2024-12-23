# This file is placed in the Public Domain.
# pylint: disable=C,R0903,W0105,W0719,E1101


"persistence"


import datetime
import json
import os
import pathlib
import _thread


from .object  import Object, Obj, dumps, fqn, loads, search, update
from .utils   import cdir, fntime, strip


cachelock = _thread.allocate_lock()
disklock  = _thread.allocate_lock()
findlock  = _thread.allocate_lock()
lock      = _thread.allocate_lock()
p         = os.path.join


class Config(Obj):

    fqns = []
    name = "obz"
    wdr  = os.path.expanduser("~/.{Config.name}")


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
    def typed(match):
        with cachelock:
            for key in Cache.objs:
                if match not in key:
                    continue
                yield Cache.objs.get(key)


"path"


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


def store(pth=""):
    stor = p(Config.wdr, "store", "")
    if not os.path.exists(stor):
        skel()
    return p(Config.wdr, "store", pth)


"utilities"


def find(mtc, selector=None, index=None, deleted=False, matching=False):
    clz = long(mtc)
    nrs = -1
    with findlock:
        for fnm in sorted(fns(clz), key=fntime):
            obj = Cache.get(fnm)
            if obj:
                yield (fnm, obj)
                continue
            obj = Object()
            read(obj, fnm)
            if not deleted and '__deleted__' in dir(obj) and obj.__deleted__:
                continue
            if selector and not search(obj, selector, matching):
                continue
            nrs += 1
            if index is not None and nrs != int(index):
                continue
            Cache.add(fnm, obj)
            yield (fnm, obj)


def fns(mtc=""):
    dname = ''
    with disklock:
        pth = store(mtc)
        for rootdir, dirs, _files in os.walk(pth, topdown=False):
            if dirs:
                for dname in sorted(dirs):
                    if dname.count('-') == 2:
                        ddd = p(rootdir, dname)
                        for fll in os.scandir(ddd):
                            yield strip(p(ddd, fll))


def skel():
    stor = p(Config.wdr, "store", "")
    path = pathlib.Path(stor)
    path.mkdir(parents=True, exist_ok=True)
    return path


def types():
    return os.listdir(store())


"methods"


def read(obj, pth):
    with disklock:
        pth2 = store(pth)
        fetch(obj, pth2)
        return os.sep.join(pth.split(os.sep)[-3:])


def ident(obj):
    return p(fqn(obj), *str(datetime.datetime.now()).split())


def last(obj, selector=None):
    if selector is None:
        selector = {}
    result = sorted(
                    find(fqn(obj), selector),
                    key=lambda x: fntime(x[0])
                   )
    res = None
    if result:
        inp = result[-1]
        update(obj, inp[-1])
        res = inp[0]
    return res


def fetch(obj, pth):
    with lock:
        with open(pth, 'r', encoding='utf-8') as ofile:
            try:
                obj2 = loads(ofile.read())
                update(obj, obj2)
            except json.decoder.JSONDecodeError as ex:
                raise Exception(pth) from ex


def write(obj, pth=None):
    if pth is None:
        pth = ident(obj)
    with disklock:
        pth2 = store(pth)
        sync(obj, pth2)
        return pth


def sync(obj, pth):
    with lock:
        cdir(pth)
        txt = dumps(obj, indent=4)
        with open(pth, 'w', encoding='utf-8') as ofile:
            ofile.write(txt)


"interface"


def __dir__():
    return (
        'Config',
        'Obj',
        'find',
        'fetch',
        'last',
        'read',
        'sync',
        'write'
    )
