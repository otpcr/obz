# This file is placed in the Public Domain.
# pylint: disable=C,R0902,W0613,W0223


"client"


import queue
import threading


from .command import Default, command
from .run     import Reactor, launch


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


class Event(Default):

    def __init__(self):
        Default.__init__(self)
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


def __dir__():
    return (
        'Client',
        'Event',
        'Output'
    )
