"""
\brief tests related to abstractvalue.py
"""

import unittest
from uuid import uuid4

from pygmodels.value.valuetype.abstractvalue import PyValue


class BaseGraphTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = True
        self.v2 = 1
        self.v3 = 1.5
        self.v4 = "hello"
        self.v5 = frozenset([1, 3])
        self.v6 = lambda x: x

        def foo(x):
            return x

        self.v7 = foo
        self.v8 = [1, 3]
        self.v9 = set([1, 3])
        self.v10 = dict(a=4, b=5)

    def test_pyvalue_1(self):
        """"""
        self.assertTrue(isinstance(self.v1, PyValue))

    def test_pyvalue_2(self):
        """"""
        self.assertTrue(isinstance(self.v2, PyValue))

    def test_pyvalue_3(self):
        """"""
        self.assertTrue(isinstance(self.v3, PyValue))

    def test_pyvalue_4(self):
        """"""
        self.assertTrue(isinstance(self.v4, PyValue))

    def test_pyvalue_5(self):
        """"""
        self.assertTrue(isinstance(self.v5, PyValue))

    def test_pyvalue_6(self):
        """"""
        self.assertTrue(isinstance(self.v6, PyValue))

    def test_pyvalue_7(self):
        """"""
        self.assertTrue(isinstance(self.v7, PyValue))

    def test_pyvalue_8(self):
        """"""
        self.assertFalse(isinstance(self.v8, PyValue))

    def test_pyvalue_9(self):
        """"""
        self.assertFalse(isinstance(self.v9, PyValue))

    def test_pyvalue_10(self):
        """"""
        self.assertFalse(isinstance(self.v10, PyValue))


if __name__ == "__main__":
    unittest.main()
