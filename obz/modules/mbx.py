# This file is placed in the Public Domain.
# pylint: disable=C0103,C0115,C0116,C0209,C0301,R0903,W0105,E0402


"mailbox"


import mailbox
import os
import time


from ..objects import Object, fmt, update
from ..persist import elapsed, find, fntime, write


"email"


class Email(Object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ""


"utility"


def todate(date):
    date = date.replace("_", ":")
    res = date.split()
    ddd = ""
    try:
        if "+" in res[3]:
            raise ValueError
        if "-" in res[3]:
            raise ValueError
        int(res[3])
        ddd = "{:4}-{:#02}-{:#02} {:6}".format(res[3], MONTH[res[2]], int(res[1]), res[4])
    except (IndexError, KeyError, ValueError) as ex:
        try:
            if "+" in res[4]:
                raise ValueError from ex
            if "-" in res[4]:
                raise ValueError from ex
            int(res[4])
            ddd = "{:4}-{:#02}-{:02} {:6}".format(res[4], MONTH[res[1]], int(res[2]), res[3])
        except (IndexError, KeyError, ValueError):
            try:
                ddd = "{:4}-{:#02}-{:02} {:6}".format(res[2], MONTH[res[1]], int(res[0]), res[3])
            except (IndexError, KeyError):
                try:
                    ddd = "{:4}-{:#02}-{:02}".format(res[2], MONTH[res[1]], int(res[0]))
                except (IndexError, KeyError):
                    try:
                        ddd = "{:4}-{:#02}".format(res[2], MONTH[res[1]])
                    except (IndexError, KeyError):
                        try:
                            ddd = "{:4}".format(res[2])
                        except (IndexError, KeyError):
                            ddd = ""
    return ddd


"commands"


def cor(event):
    if not event.args:
        event.reply("cor <email>")
        return
    nr = -1
    for _fn, email in find("email", {"From": event.args[0]}):
        nr += 1
        txt = ""
        if len(event.args) > 1:
            txt = ",".join(event.args[1:])
        else:
            txt = "From,Subject"
        event.reply("%s %s %s" % (nr, fmt(email, txt, plain=True), elapsed(time.time() - fntime(email.__stp__))))


def eml(event):
    nrs = -1
    result = sorted(find("email", event.gets), key=lambda x: todate(getattr(x[1], "Date", "")))
    if event.index:
        o = result[event.index][1]
        tme = getattr(o, "Date", "")
        event.reply(f'{event.index} {format(o, ["From", "Subject"] + event.args)} {elapsed(time.time() - fntime(tme))}')
    else:
        for fnm, o in result:
            nrs += 1
            event.reply(f'{nrs} {format(o, ["From", "Subject"])} {elapsed(time.time() - fntime(fnm))}')
    if nrs == -1:
        event.reply("no emails found.")


def mbx(event):
    if not event.args:
        event.reply("mbx <path>")
        return
    fn = os.path.expanduser(event.args[0])
    event.reply("reading from %s" % fn)
    nr = 0
    if os.path.isdir(fn):
        thing = mailbox.Maildir(fn, create=False)
    elif os.path.isfile(fn):
        thing = mailbox.mbox(fn, create=False)
    else:
        return
    try:
        thing.lock()
    except FileNotFoundError:
        pass
    for m in thing:
        o = Email()
        update(o, dict(m._headers)) # pylint: disable=W0212
        o.text = ""
        for payload in m.walk():
            if payload.get_content_type() == 'text/plain':
                o.text += payload.get_payload()
        o.text = o.text.replace("\\n", "\n")
        write(o)
        nr += 1
    if nr:
        event.reply("ok %s" % nr)


"data"


MONTH = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}
