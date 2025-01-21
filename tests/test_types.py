# This file is placed in the Public Domain.
# pylint: disable=C,R,W0201,W1503


"no tests"


import unittest


from obz.objects import Object, dumps, loads


class A(Object):

    pass


class B:

    def __init__(self):
        self.a = A()
        self.a.a = A()


class TestTypes(unittest.TestCase):

    def test_none(self):
        a = True
        res = loads(dumps(a))
        self.assertEqual(res, True)

    def test_string(self):
        a = "yo!"
        res = loads(dumps(a))
        self.assertEqual(res, "yo!")

    def test_integer(self):
        a = 1
        res = loads(dumps(a))
        self.assertEqual(res, 1)

    def test_dict(self):
        a = {"a": "b"}
        res = loads(dumps(a))
        self.assertEqual(res.a, "b")

    def test_boolean(self):
        a = False
        res = loads(dumps(a))
        self.assertEqual(res, False)

    def test_compsite(self):
        b = B()
        b.a.a.b = 10
        res = loads(dumps(b))
        self.assertEqual(res.a.a.b, 10)
