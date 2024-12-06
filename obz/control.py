# This file is placed in the Public Domain.
# pylint: disable=C0115,C0116,C0415,R0903,R0912,R0915,W0105,W0718,E0402


"main"


import readline
import sys
import termios
import time


from .persist import Config
from .runtime import Client, Commands, Event
from .runtime import command, errors, forever, later, parse, scan


Cfg = Config()


class CLI(Client):

    def raw(self, txt):
        print(txt)


class Console(CLI):

    "Console"

    def announce(self, txt):
        "echo text."
        self.raw(txt)

    def callback(self, evt):
        "wait for callback."
        Client.callback(self, evt)
        evt.wait()

    def poll(self):
        "poll console and create event."
        evt = Event()
        evt.txt = input("> ")
        evt.type = "command"
        return evt


def banner():
    tme = time.ctime(time.time()).replace("  ", " ")
    print(f"{Cfg.name.upper()} since {tme}")


def wrap(func):
    old = None
    try:
        old = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        print("")
    except Exception as ex:
        later(ex)
    finally:
        if old:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)


def wrapped():
    wrap(main)
    for line in errors():
        print(line)


def srv(event):
    import getpass
    name = getpass.getuser()
    event.reply(TXT % (Cfg.name.upper(), name, name, name, Cfg.name.upper()))


def main():
    Commands.add(srv)
    parse(Cfg, " ".join(sys.argv[1:]))
    from .modules import face
    scan(face)
    if "c" in Cfg.opts:
        banner()
        csl = Console()
        csl.start()
        forever()
    else:
        evt = Event()
        evt.type = "command"
        evt.txt = Cfg.otxt
        csl = CLI()
        command(csl, evt)
        evt.wait()


TXT = """[Unit]
Description=%s
After=network-online.target

[Service]
Type=simple
User=%s
Group=%s
ExecStart=/home/%s/.local/bin/%ss

[Install]
WantedBy=multi-user.target"""


if __name__ == "__main__":
    wrapped()
