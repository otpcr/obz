# This file is in the Public Domain.
# pylint: disable=C0116,C0415,E0402


"service"


import os


from .command import scan
from .persist import Config, pidfile, pidname
from .runtime import errors, forever, wrap


def privileges():
    import getpass
    import pwd
    pwnam2 = pwd.getpwnam(getpass.getuser())
    os.setgid(pwnam2.pw_gid)
    os.setuid(pwnam2.pw_uid)



def service():
    privileges()
    pidfile(pidname(Config.name))
    from .modules import face as mods
    scan(mods, init=True)
    forever()


def wrapped():
    wrap(service)
    for line in errors():
        print(line)


if __name__ == "__main__":
    wrapped()
