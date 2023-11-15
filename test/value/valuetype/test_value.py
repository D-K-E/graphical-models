"""
\brief tests related value.py
"""
import unittest
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.value.valuetype.value import StringValue
from pygmodels.value.valuetype.value import ContainerValue
from pygmodels.value.valuetype.value import CallableValue
from pygmodels.value.valuetype.value import SetValue
from pygmodels.utils import is_all_type


class NumericValueTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = NumericValue(v=1)
        self.v2 = NumericValue(v=2.1)
        self.v3 = NumericValue(v=False)
        self.v4 = NumericValue(v=2)

    def test_is_numeric(self):
        """"""
        self.assertTrue(self.v1.is_numeric())
        self.assertTrue(self.v2.is_numeric())
        self.assertTrue(self.v3.is_numeric())

    def test_is_string(self):
        """"""
        self.assertFalse(self.v1.is_string())
        self.assertFalse(self.v2.is_string())
        self.assertFalse(self.v3.is_string())

    def test_is_container(self):
        """"""
        self.assertFalse(self.v1.is_container())
        self.assertFalse(self.v2.is_container())
        self.assertFalse(self.v3.is_container())

    def test_is_callable(self):
        """"""
        self.assertFalse(self.v1.is_callable())
        self.assertFalse(self.v2.is_callable())
        self.assertFalse(self.v3.is_callable())

    def test_instantiate(self):
        """"""
        try:
            v = NumericValue(v="foo")
            check = False
        except:
            check = True
        #
        self.assertTrue(check)

    def test_add(self):
        """"""
        v = self.v1 + self.v2
        self.assertEqual(round(v.value, 2), 3.1)

    def test_sub(self):
        """"""
        v = self.v2 - self.v1
        self.assertEqual(round(v.value, 2), 1.1)

    def test_rsub(self):
        """"""
        v = 1 - self.v1
        self.assertEqual(v.value, 0)

    def test_mul(self):
        """"""
        v = self.v2 * self.v1
        self.assertEqual(v.value, 2.1)

    def test_truediv(self):
        """"""
        v = self.v2 / self.v1
        self.assertEqual(v.value, 2.1)

    def test_floordiv(self):
        """"""
        v = self.v2 // self.v1
        self.assertEqual(v.value, 2)

    def test_mod(self):
        """"""
        v = self.v2 % 2
        self.assertEqual(round(v.value, 3), 0.1)

    def test_rtruediv(self):
        """"""
        v = 1 / self.v4
        self.assertEqual(round(v.value, 3), 0.5)

    def test_rfloordiv(self):
        """"""
        v = 1 / self.v1
        self.assertEqual(v.value, 1)

    def test_rmod(self):
        """"""
        v = 3 % self.v1
        self.assertEqual(v.value, 0)

    def test_rpow(self):
        """"""
        v = 3**self.v1
        self.assertEqual(v.value, 3)

    def test_lt(self):
        """"""
        v = self.v1 < self.v2
        self.assertEqual(v.value, True)

    def test_le(self):
        """"""
        v = self.v1 <= self.v2
        self.assertEqual(v.value, True)

    def test_gt(self):
        """"""
        v = self.v2 > self.v1
        self.assertEqual(v.value, True)

    def test_ge(self):
        """"""
        v = self.v2 >= self.v1
        self.assertEqual(v.value, True)

    def test_eq(self):
        """"""
        v = self.v2 == self.v1
        self.assertEqual(v.value, False)

    def test_ne(self):
        """"""
        v = self.v2 != self.v1
        self.assertEqual(v.value, True)


class StringValueTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = StringValue(v="foo")

    def test_is_numeric(self):
        """"""
        self.assertFalse(self.v1.is_numeric())

    def test_is_string(self):
        """"""
        self.assertTrue(self.v1.is_string())

    def test_is_container(self):
        """"""
        self.assertFalse(self.v1.is_container())

    def test_is_callable(self):
        """"""
        self.assertFalse(self.v1.is_callable())

    def test_instantiate(self):
        """"""
        try:
            v = StringValue(v=1)
            check = False
        except:
            check = True
        #
        self.assertTrue(check)


class ContainerValueTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = ContainerValue(v=tuple([NumericValue(1), NumericValue(2)]))
        self.v2 = ContainerValue(v=frozenset([StringValue("foo"), StringValue("bar")]))

    def test_is_numeric(self):
        """"""
        self.assertFalse(self.v1.is_numeric())
        self.assertFalse(self.v2.is_numeric())

    def test_is_string(self):
        """"""
        self.assertFalse(self.v1.is_string())
        self.assertFalse(self.v2.is_string())

    def test_is_container(self):
        """"""
        self.assertTrue(self.v1.is_container())
        self.assertTrue(self.v2.is_container())

    def test_is_callable(self):
        """"""
        self.assertFalse(self.v1.is_callable())
        self.assertFalse(self.v2.is_callable())

    def test_instantiate(self):
        """"""
        try:
            v = ContainerValue(v=[1, 3])
            check = False
        except:
            check = True
        #
        self.assertTrue(check)


class CallableValueTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = CallableValue(v=lambda x: x)

        def foo(x):
            return x

        self.v2 = CallableValue(v=foo)

    def test_is_numeric(self):
        """"""
        self.assertFalse(self.v1.is_numeric())
        self.assertFalse(self.v2.is_numeric())

    def test_is_string(self):
        """"""
        self.assertFalse(self.v1.is_string())
        self.assertFalse(self.v2.is_string())

    def test_is_container(self):
        """"""
        self.assertFalse(self.v1.is_container())
        self.assertFalse(self.v2.is_container())

    def test_is_callable(self):
        """"""
        self.assertTrue(self.v1.is_callable())
        self.assertTrue(self.v2.is_callable())

    def test_instantiate(self):
        """"""
        try:
            v = CallableValue(v=[1, 3])
            check = False
        except:
            check = True
        #
        self.assertTrue(check)


class SetValueTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = SetValue(v=StringValue(v="foo"), set_id="bar")

    def test_is_numeric(self):
        """"""
        self.assertFalse(self.v1.is_numeric())

    def test_is_string(self):
        """"""
        self.assertTrue(self.v1.is_string())

    def test_is_container(self):
        """"""
        self.assertFalse(self.v1.is_container())

    def test_is_callable(self):
        """"""
        self.assertFalse(self.v1.is_callable())

    def test_belongs_to(self):
        """"""
        self.assertEqual(self.v1.belongs_to, "bar")

    def test_value(self):
        """"""
        self.assertEqual(self.v1.value, "foo")

    def test_fetch(self):
        """"""
        f = self.v1.fetch()
        v = StringValue(v="foo")
        self.assertEqual(f, v)

    def test_instantiate(self):
        """"""
        try:
            v = SetValue(v=[1, 3])
            check = False
        except:
            check = True
        #
        self.assertTrue(check)


if __name__ == "__main__":
    unittest.main()
