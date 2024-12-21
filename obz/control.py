# This file is placed in the Public Domain.
# pylint: disable=C0115,C0116,C0415,R0903,R0912,R0915,W0105,W0718,E0402


"main"


import sys


from .client  import Client, Event
from .command import Commands, command, parse, scan
from .persist import Config
from .runtime import errors, plain


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


Cfg = Config()


class CLI(Client):

    def raw(self, txt):
        print(txt)


def wrapped():
    plain(main)
    for line in errors():
        print(line)


def srv(event):
    import getpass
    name = getpass.getuser()
    event.reply(TXT % (Cfg.name.upper(), name, name, name, Cfg.name))


def main():
    Commands.add(srv)
    parse(Cfg, " ".join(sys.argv[1:]))
    from .modules import face
    scan(face)
    evt = Event()
    evt.type = "command"
    evt.txt = Cfg.otxt
    csl = CLI()
    command(csl, evt)
    evt.wait()


if __name__ == "__main__":
    wrapped()
