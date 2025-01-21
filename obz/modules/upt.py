# This file is placed in the Public Domain.


"uptime"


import time


from obz.locater import elapsed


STARTTIME = time.time()


def upt(event):
    """ show uptime. """
    event.reply(elapsed(time.time()-STARTTIME))
