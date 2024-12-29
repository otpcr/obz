# This file is placed in the Public Domain.
# pylint: disable=C


"commands"


from ..client import Commands
from ..method import keys


def cmd(event):
    event.reply(",".join(sorted(keys(Commands.cmds))))
