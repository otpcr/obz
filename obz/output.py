# This file is placed in the Public Domain.
# pylint: disable=C,R0903,W0105,W0613,E0402


"output buffer"


import queue
import threading


from .thread import launch


"output"


class Output:

    cache = {}

    def __init__(self):
        self.oqueue = queue.Queue()
        self.dostop = threading.Event()

    def oput(self, channel, txt):
        self.oqueue.put((channel, txt))

    def output(self):
        while not self.dostop.is_set():
            (channel, txt) = self.oqueue.get()
            if channel is None and txt is None:
                self.oqueue.task_done()
                break
            self.dosay(channel, txt)
            self.oqueue.task_done()

    def start(self):
        launch(self.output)

    def stop(self):
        self.oqueue.join()
        self.dostop.set()
        self.oqueue.put((None, None))

    def wait(self):
        self.dostop.wait()


"interface"


def __dir__():
    return (
        'Output',
    )
