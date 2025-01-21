# This file is placed in the Public Domain.


"clients"


import queue
import threading


from obz.command import command
from obz.objects import Default
from obz.reactor import Reactor
from obz.threads import launch


class Client(Reactor):

    def __init__(self):
        Reactor.__init__(self)
        self.register("command", command)
        Fleet.add(self)

    def display(self, evt):
        for txt in evt.result:
            self.raw(txt)

    def raw(self, txt):
        raise NotImplementedError("raw")


class Config(Default):

    name = Default.__module__.rsplit(".", maxsplit=2)[-2]
    

class Fleet:

    bots = {}

    @staticmethod
    def add(bot):
        Fleet.bots[repr(bot)] = bot

    @staticmethod
    def announce(txt):
        for bot in Fleet.bots:
            bot.announce(txt)

    def first(self):
        if Fleet.bots:
            return Fleet.bots.values()[0]

    @staticmethod
    def get(name):
        return Fleet.bots.get(name, None)


class Output:

    cache = {}

    def __init__(self):
        self.oqueue = queue.Queue()
        self.dostop = threading.Event()

    def display(self, evt):
        for txt in evt.result:
            self.oput(evt.channel, txt)

    def dosay(self, channel, txt):
        raise NotImplementedError("dosay")

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


def __dir__():
    return (
        'Client',
        'Config',
        'Fleet',
        'Output'
    )
