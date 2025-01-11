# This file is placed in the Public Domain.
# pylint: disable=C


"configuration"


from .object import Obj


"config"


class Config(Obj):

    name = Obj.__module__.split(".")[0]


"interface"


def __dir__():
    return (
        'Config',
    )
