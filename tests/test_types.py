# This file is placed in the Public Domain.
# pylint: disable=C,R,W1503


"no tests"


import unittest


from obz.json import dumps, loads, typed


class A:

    pass


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

    def test_object(self):
        a = A()
        typed(a, dumps(a))
        self.assertEqual(type(a), A)
