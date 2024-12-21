# This file is placed in the Public Domain.
# pylint: disable=C,W0718


"main"


import sys
import time


from .client  import Client, Event
from .command import parse, scan
from .persist import Config
from .runtime import errors, forever, wrap


cfg = Config()


class Console(Client):

    def announce(self, txt):
        self.raw(txt)

    def callback(self, evt):
        Client.callback(self, evt)
        evt.wait()

    def poll(self):
        evt = Event()
        evt.txt = input("> ")
        evt.type = "command"
        return evt

    def raw(self, txt):
        print(txt)


def banner():
    tme = time.ctime(time.time()).replace("  ", " ")
    print(f"{cfg.name.upper()} since {tme}")


def wrapped():
    wrap(main)
    for line in errors():
        print(line)


def main():
    parse(cfg, " ".join(sys.argv[1:]))
    if "v" in cfg.opts:
        banner()
    from .modules import face
    for mod, thr in scan(face, init="i" in cfg.opts, disable=cfg.sets.dis):
        if "v" in cfg.opts and "output" in dir(mod):
            mod.output = print
        if thr and "w" in cfg.opts:
            thr.join()
    csl = Console()
    csl.start()
    forever()


if __name__ == "__main__":
    wrapped()
