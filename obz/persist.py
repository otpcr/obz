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


def types():
    return os.listdir(store())


"utilities"


def cdir(pth):
    path = pathlib.Path(pth)
    path.parent.mkdir(parents=True, exist_ok=True)


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


def fntime(daystr):
    daystr = daystr.replace('_', ':')
    datestr = ' '.join(daystr.split(os.sep)[-2:])
    if '.' in datestr:
        datestr, rest = datestr.rsplit('.', 1)
    else:
        rest = ''
    timed = time.mktime(time.strptime(datestr, '%Y-%m-%d %H:%M:%S'))
    if rest:
        timed += float('.' + rest)
    return timed


def laps(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    yea = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    yeas = int(nsec/yea)
    nsec -= yeas*yea
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    nsec -= int(minute*minutes)
    sec = int(nsec)
    if yeas:
        txt += f"{yeas}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def pidfile(filename):
    if os.path.exists(filename):
        os.unlink(filename)
    path2 = pathlib.Path(filename)
    path2.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fds:
        fds.write(str(os.getpid()))


def skel():
    stor = p(Config.wdr, "store", "")
    path = pathlib.Path(stor)
    path.mkdir(parents=True, exist_ok=True)
    return path


def strip(pth, nmr=3):
    return os.sep.join(pth.split(os.sep)[-nmr:])


"methods"


def edit(obj, setter, skip=False):
    for key, val in items(setter):
        if skip and val == "":
            continue
        try:
            setattr(obj, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(obj, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(obj, key, True)
        elif val in ["False", "false"]:
            setattr(obj, key, False)
        else:
            setattr(obj, key, val)


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


def match(obj, txt):
    for key in keys(obj):
        if txt in key:
            yield key


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


def read(obj, pth):
    with disklock:
        pth2 = store(pth)
        fetch(obj, pth2)
        return os.sep.join(pth.split(os.sep)[-3:])


def search(obj, selector, matching=None):
    res = False
    if not selector:
        return res
    for key, value in items(selector):
        val = getattr(obj, key, None)
        if not val:
            continue
        if matching and value == val:
            res = True
        elif str(value).lower() in str(val).lower():
            res = True
        else:
            res = False
            break
    return res


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
