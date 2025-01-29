# This file is placed in the Public Domain.
# pylint: disable=C0116,E0402


"uptime"


import time


from ..persist import elapsed
from ..runtime import STARTTIME


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))
