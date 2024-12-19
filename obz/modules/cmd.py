# This file is placed in the Public Domain.
# pylint: disable=C


"commands"


from ..object  import keys
from ..command import Commands


def cmd(event):
    event.reply(",".join(sorted(keys(Commands.cmds))))
