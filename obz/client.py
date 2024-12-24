# This file is placed in the Public Domain.
# pylint: disable=C,R,W0223,W0613,W0718


"client"


import queue
import threading


from .object  import Obj
from .runtime import Commands, Reactor, later, launch


class Output:

    cache = {}

    def __init__(self):
        self.oqueue = queue.Queue()

    def display(self, evt):
        for txt in evt.result:
            self.raw(txt)

    def dosay(self, channel, txt):
        self.raw(txt)

    def oput(self, channel, txt):
        self.oqueue.put((channel, txt))

    def output(self):
        while True:
            (channel, txt) = self.oqueue.get()
            if channel is None and txt is None:
                self.oqueue.task_done()
                break
            self.dosay(channel, txt)
            self.oqueue.task_done()

    def raw(self, txt):
        raise NotImplementedError

    def start(self):
        launch(self.output)

    def stop(self):
        self.oqueue.put((None, None))

    def wait(self):
        self.oqueue.join()


class Client(Output, Reactor):

    def __init__(self):
        Output.__init__(self)
        Reactor.__init__(self)
        self.register("command", command)

    def start(self):
        Output.start(self)
        Reactor.start(self)


class Event(Obj):

    def __init__(self):
        Obj.__init__(self)
        self._ready = threading.Event()
        self._thr   = None
        self.result = []
        self.type   = "event"
        self.txt    = ""

    def __str__(self):
        return str(self.__dict__)

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result.append(txt)

    def wait(self):
        self._ready.wait()
        if self._thr:
            self._thr.join()


def command(bot, evt):
    parse(evt, evt.txt)
    if "ident" in dir(bot):
        evt.orig = bot.ident
    func = Commands.cmds.get(evt.cmd, None)
    if func:
        try:
            func(evt)
            bot.display(evt)
        except Exception as ex:
            later(ex)
    evt.ready()


def parse(obj, txt=None) -> None:
    if txt is None:
        txt = ""
    args = []
    obj.args    = []
    obj.cmd     = ""
    obj.gets    = Obj()
    obj.hasmods = False
    obj.index   = None
    obj.mod     = ""
    obj.opts    = ""
    obj.result  = []
    obj.sets    = Obj()
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
            val = getattr(obj.gets, key, None)
            if val:
                value = val + "," + value
                setattr(obj.gets, key, value)
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                obj.hasmods = True
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


def __dir__():
    return (
        'Client',
        'Event',
        'Output',
        'command',
        'parse'
    )
