# This file is placed in the Public Domain.
# pylint: disable=C


"composite"


import unittest


from obz.object import Object


class TestComposite(unittest.TestCase):

    def testcomposite(self):
        obj = Object()
        obj.obj = Object()
        obj.obj.abc = "test"
        self.assertEqual(obj.obj.abc, "test")
