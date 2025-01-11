# This file is placed in the Public Domain.
# pylint: disable=C,R0903,W0105,W0718,E0402


"timers"


import threading
import time


from .thread import launch, name


"timer"


class Timer:

    def __init__(self, sleep, func, *args, thrname=None, **kwargs):
        self.args  = args
        self.func  = func
        self.kwargs = kwargs
        self.sleep = sleep
        self.name  = thrname or kwargs.get("name", name(func))
        self.state = {}
        self.timer = None

    def run(self):
        self.state["latest"] = time.time()
        launch(self.func, *self.args)

    def start(self):
        timer = threading.Timer(self.sleep, self.run)
        timer.name   = self.name
        timer.sleep  = self.sleep
        timer.state  = self.state
        timer.func   = self.func
        timer.state["starttime"] = time.time()
        timer.state["latest"]    = time.time()
        timer.start()
        self.timer   = timer

    def stop(self):
        if self.timer:
            self.timer.cancel()


"repeater"


class Repeater(Timer):

    def run(self):
        launch(self.start)
        super().run()


"interface"


def __dir__():
    return (
        'Repeater',
        'Timer'
    )
