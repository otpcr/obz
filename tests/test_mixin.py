# This file is placed in the Public Domain.
# pylint: disable=C,R


"mixin"


import unittest


from obz.object import Object


class Mix:

    a = "b"


class Mixin(Mix, Object):

    pass


class TestMixin(unittest.TestCase):

    def test_mixin(self):
        mix = Mixin()
        self.assertTrue(isinstance(mix, Mixin))
