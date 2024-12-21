# This file is placed in the Public Domain.
# pylint: disable=C,W0212


"daemon"


from .command import scan
from .persist import Config, pidfile, pidname
from .runtime import daemon, errors, forever, privileges, wrap


def wrapped():
    wrap(main)
    for line in errors():
        print(line)


def main():
    daemon(True)
    privileges()
    pidfile(pidname(Config.name))
    from .modules import face
    scan(face, init=True)
    forever()


if __name__ == "__main__":
    wrapped()
