# This file is placed in the Public Domain.
# pylint: disable=C,W0105


"event"


import threading
import time


from .object import Object


class Event(Object):

    def __init__(self):
        Object.__init__(self)
        self._ex    = None
        self._ready = threading.Event()
        self._thr   = None
        self.ctime  = time.time()
        self.result = []
        self.type   = "event"
        self.txt    = ""

    def __getattr__(self, key):
        return self.__dict__.get(key, "")

    def ok(self):
        self.reply(f"ok {self.txt}")

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result.append(txt)

    def wait(self):
        self._ready.wait()
        if self._thr:
            self._thr.join()


"interface"


def __dir__():
    return (
        'Event',
    )
