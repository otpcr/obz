# This file is placed in the Public Domain.
# pylint: disable=C,R0903,W0105,W0613,E0402


"client"


from .cache   import Fleet
from .command import command
from .output  import Output
from .reactor import Reactor


"client"


class Client(Reactor):

    def __init__(self):
        Reactor.__init__(self)
        Fleet.add(self)
        self.register("command", command)

    def display(self, evt):
        for txt in evt.result:
            self.raw(txt)

    def raw(self, txt):
        raise NotImplementedError("raw")


"buffer"


class Buffered(Output, Client):

    def __init__(self):
        Output.__init__(self)
        Client.__init__(self)

    def display(self, evt):
        for txt in evt.result:
            self.oput(evt.channel, txt)

    def dosay(self, channel, txt):
        self.raw(txt)

    def raw(self, txt):
        raise NotImplementedError("raw")

    def stop(self):
        Output.stop(self)
        Client.stop(self)
    
    def start(self):
        Output.start(self)
        Client.start(self)

    def wait(self):
        Output.wait(self)
        Client.wait(self)


"interface"


def __dir__():
    return (
        'Buffered',
        'Client'
    )
