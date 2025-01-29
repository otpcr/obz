# This file is placed in the Public Domain.
# pylint: disable=C0115,C0116,R0903,R0912,W0105,W0612,W0613,W0718,E0402


"command"


import importlib
import inspect
import os
import threading


from .runtime import Default, Fleet, later, launch


try:
    from .lookups import NAMES
except Exception as ex:
    later(ex)
    NAMES = {}


def locked(func, *args, **kwargs):

    def locker(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)

    return locker


lock = threading.RLock()


"commands"


class Commands:

    cmds = {}
    names = NAMES

    @staticmethod
    def add(func, mod=None):
        Commands.cmds[func.__name__] = func
        if mod:
            Commands.names[func.__name__] = mod.__name__

    @staticmethod
    def get(cmd):
        return Commands.cmds.get(cmd, None)

    @staticmethod
    def getname(cmd):
        return Commands.names.get(cmd)

    @staticmethod
    def scan(mod):
        for key, cmdz in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmdz.__code__.co_varnames:
                Commands.add(cmdz, mod)


"table"


class Table:

    mods = {}

    @staticmethod
    def add(mod):
        Table.mods[mod.__name__] = mod

    @staticmethod
    def get(name):
        return Table.mods.get(name, None)

    @staticmethod
    def inits(names, pname):
        mods = []
        for name in spl(names):
            mname = pname + "." + name
            if not mname:
                continue
            mod = Table.load(mname)
            if not mod:
                continue
            thr = launch(mod.init)
            mods.append((mod, thr))
        return mods

    @staticmethod
    def load(name):
        pname = ".".join(name.split(".")[:-1])
        mod = Table.mods.get(name)
        if not mod:
            try:
                Table.mods[name] = mod = importlib.import_module(name, pname)
            except Exception as ex:
                later(ex)
        return mod

    @staticmethod
    def modules(path):
        return [
                x[:-3] for x in os.listdir(path)
                if x.endswith(".py") and not x.startswith("__")
               ]

    @staticmethod
    def scan(pkg, mods=""):
        res = []
        path = pkg.__path__[0]
        pname = ".".join(path.split(os.sep)[-2:])
        for nme in Table.modules(path):
            if "__" in nme:
                continue
            if mods and nme not in spl(mods):
                continue
            name = pname + "." + nme
            if not name:
                continue
            mod = Table.load(name)
            if not mod:
                continue
            Commands.scan(mod)
            res.append(mod)
        return res


"callbacks"


def command(evt):
    parse(evt)
    func = Commands.get(evt.cmd)
    if not func:
        mname = NAMES.get(evt.cmd)
        if mname:
            mod = Table.load(mname)
            Commands.scan(mod)
            func = Commands.get(evt.cmd)
    if not func:
        evt.ready()
        return
    func(evt)
    Fleet.display(evt)


"utilities"


def parse(obj, txt=None):
    if txt is None:
        if "txt" in dir(obj):
            txt = obj.txt
        else:
            txt = ""
    args = []
    obj.args    = []
    obj.cmd     = ""
    obj.gets    = Default()
    obj.index   = None
    obj.mod     = ""
    obj.opts    = ""
    obj.result  = {}
    obj.sets    = Default()
    obj.txt     = txt or ""
    obj.otxt    = obj.txt
    _nr = -1
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            setattr(obj.gets, key, value)
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            setattr(obj.sets, key, value)
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""
    return obj


def spl(txt):
    try:
        result = txt.split(',')
    except (TypeError, ValueError):
        result = txt
    return [x for x in result if x]


"interface"


def __dir__():
    return (
        'Table',
        'Commands',
        'command',
        'cmd',
        'parse',
        'spl'
    )
