# This file is placed in the Public Domain.
# pylint: disable=C0116,C0301,E0402


"slogan"


TXT = """By law, with the use of poison, killing, torturing, castrating, destroying in whole or in part,
all elderly and all handicapped (Wzd), all criminals (Wfz) and all psychiatric patients (WvGGZ)
here in the Netherlands."""


def lne(event):
    event.reply(TXT.split("\n", maxsplit=1)[0])


def slg(event):
    event.reply(TXT)
