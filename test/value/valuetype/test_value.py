"""
\brief tests related value.py
"""
import unittest
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.value.valuetype.value import NTupleValue
from pygmodels.value.valuetype.value import StringValue
from pygmodels.value.valuetype.value import ContainerValue
from pygmodels.value.valuetype.value import CallableValue
from pygmodels.value.valuetype.value import SetValue
from pygmodels.value.valuetype.value import NumericInterval
from pygmodels.value.valuetype.value import IntervalPair
from pygmodels.value.valuetype.abstractvalue import IntervalConf
from pygmodels.utils import is_all_type


class NumericValueTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = NumericValue(v=1)
        self.v2 = NumericValue(v=2.1)
        self.v3 = NumericValue(v=False)
        self.v4 = NumericValue(v=2)
        self.v5 = NumericValue(v=float("inf"))
        self.v6 = NumericValue(v=float("-inf"))

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

    def test_add_v2(self):
        """"""
        v = self.v5 + self.v2
        v2 = self.v6 + self.v2
        self.assertEqual(v.value, float("inf"))
        self.assertEqual(v2.value, float("-inf"))

    def test_add_v3(self):
        """"""
        try:
            v = self.v6 + self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_add_v4(self):
        """"""
        try:
            v = self.v5 + self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_radd_v2(self):
        """"""
        v = self.v5 + 1
        v2 = self.v6 + 12
        self.assertEqual(v.value, float("inf"))
        self.assertEqual(v2.value, float("-inf"))

    def test_radd_v3(self):
        """"""
        try:
            v = float("-inf") + self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_radd_v4(self):
        """"""
        try:
            v = float("inf") + self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_sub(self):
        """"""
        v = self.v2 - self.v1
        self.assertEqual(round(v.value, 2), 1.1)

    def test_sub_v2(self):
        """"""
        v = self.v5 - self.v2
        v2 = self.v6 - self.v2
        self.assertEqual(v.value, float("inf"))
        self.assertEqual(v2.value, float("-inf"))

    def test_sub_v3(self):
        """"""
        v = self.v5 - self.v6
        self.assertEqual(v, float("inf"))

    def test_sub_v4(self):
        """"""
        v = self.v6 - self.v5
        self.assertEqual(v, float("-inf"))

    def test_sub_v5(self):
        """"""
        try:
            v = self.v5 - self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_sub_v6(self):
        """"""
        try:
            v = self.v6 - self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rsub(self):
        """"""
        v = 1 - self.v1
        self.assertEqual(v.value, 0)

    def test_rsub_v2(self):
        """"""
        v = 2 - self.v5
        v2 = 2 - self.v6
        self.assertEqual(v.value, float("-inf"))
        self.assertEqual(v2.value, float("inf"))

    def test_rsub_v3(self):
        """"""
        v = float("inf") - self.v6
        self.assertEqual(v, float("inf"))

    def test_rsub_v4(self):
        """"""
        v = float("-inf") - self.v5
        self.assertEqual(v, float("-inf"))

    def test_rsub_v5(self):
        """"""
        try:
            v = float("inf") - self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rsub_v6(self):
        """"""
        try:
            v = float("-inf") - self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_mul(self):
        """"""
        v = self.v2 * self.v1
        self.assertEqual(v.value, 2.1)

    def test_mul_v2(self):
        """"""
        v = self.v5 * self.v2
        v2 = self.v6 * self.v2
        self.assertEqual(v.value, float("inf"))
        self.assertEqual(v2.value, float("-inf"))

    def test_mul_v3(self):
        """"""
        v = self.v5 * self.v6
        self.assertEqual(v, float("-inf"))

    def test_mul_v4(self):
        """"""
        v = self.v6 * self.v5
        self.assertEqual(v, float("-inf"))

    def test_mul_v5(self):
        """"""
        v = self.v5 * self.v5
        self.assertEqual(v, float("inf"))

    def test_mul_v6(self):
        """"""
        v = self.v6 * self.v6
        self.assertEqual(v, float("inf"))

    def test_mul_v7(self):
        """"""
        v = NumericValue(0) * self.v5
        self.assertEqual(v.value, 0)

    def test_mul_v8(self):
        """"""
        v = NumericValue(0) * self.v6
        self.assertEqual(v.value, 0)

    def test_rmul(self):
        """"""
        v = 2.1 * self.v1
        self.assertEqual(v.value, 2.1)

    def test_rmul_v2(self):
        """"""
        v = float("inf") * self.v2
        v2 = float("-inf") * self.v2
        self.assertEqual(v.value, float("inf"))
        self.assertEqual(v2.value, float("-inf"))

    def test_rmul_v3(self):
        """"""
        v = float("inf") * self.v6
        self.assertEqual(v, float("-inf"))

    def test_rmul_v4(self):
        """"""
        v = float("-inf") * self.v5
        self.assertEqual(v, float("-inf"))

    def test_rmul_v5(self):
        """"""
        v = float("inf") * self.v5
        self.assertEqual(v, float("inf"))

    def test_rmul_v6(self):
        """"""
        v = float("-inf") * self.v6
        self.assertEqual(v, float("inf"))

    def test_rmul_v7(self):
        """"""
        v = 0 * self.v5
        self.assertEqual(v.value, 0)

    def test_rmul_v8(self):
        """"""
        v = 0 * self.v6
        self.assertEqual(v.value, 0)

    def test_truediv(self):
        """"""
        v = self.v2 / self.v1
        self.assertEqual(v.value, 2.1)

    def test_truediv_v2(self):
        """"""
        try:
            v = self.v5 / self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_truediv_v3(self):
        """"""
        try:
            v = self.v6 / self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_truediv_v4(self):
        """"""
        try:
            v = self.v5 / self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_truediv_v5(self):
        """"""
        try:
            v = self.v6 / self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_floordiv(self):
        """"""
        v = self.v2 // self.v1
        self.assertEqual(v.value, 2)

    def test_floordiv_v2(self):
        """"""
        try:
            v = self.v5 // self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_floordiv_v3(self):
        """"""
        try:
            v = self.v6 // self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_floordiv_v4(self):
        """"""
        try:
            v = self.v5 // self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_floordiv_v5(self):
        """"""
        try:
            v = self.v6 // self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_mod(self):
        """"""
        v = self.v2 % 2
        self.assertEqual(round(v.value, 3), 0.1)

    def test_rtruediv(self):
        """"""
        v = 1 / self.v4
        self.assertEqual(round(v.value, 3), 0.5)

    def test_rtruediv_v2(self):
        """"""
        try:
            v = float("inf") / self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rtruediv_v3(self):
        """"""
        try:
            v = float("-inf") / self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rtruediv_v4(self):
        """"""
        try:
            v = float("inf") / self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rtruediv_v5(self):
        """"""
        try:
            v = float("-inf") / self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rfloordiv(self):
        """"""
        v = 1 / self.v1
        self.assertEqual(v.value, 1)

    def test_rfloordiv_v2(self):
        """"""
        try:
            v = float("inf") // self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rfloordiv_v3(self):
        """"""
        try:
            v = float("-inf") // self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rfloordiv_v4(self):
        """"""
        try:
            v = float("inf") // self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rfloordiv_v5(self):
        """"""
        try:
            v = float("-inf") // self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rmod(self):
        """"""
        v = 3 % self.v1
        self.assertEqual(v.value, 0)

    def test_pow(self):
        """"""
        v = self.v1 ** NumericValue(3)
        self.assertEqual(v.value, 1)

    def test_pow_v2(self):
        """"""
        v = self.v5 ** NumericValue(3)
        self.assertEqual(v.value, float("inf"))

    def test_pow_v3(self):
        """"""
        v = self.v5**self.v5
        self.assertEqual(v.value, float("inf"))

    def test_pow_v4(self):
        """"""
        try:
            v = self.v5**self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_pow_v5(self):
        """"""
        try:
            v = self.v6**self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_pow_v6(self):
        """"""
        try:
            v = self.v6**self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rpow(self):
        """"""
        v = 3**self.v1
        self.assertEqual(v.value, 3)

    def test_rpow_v2(self):
        """"""
        v = float("inf") ** NumericValue(3)
        self.assertEqual(v.value, float("inf"))

    def test_rpow_v3(self):
        """"""
        v = float("inf") ** self.v5
        self.assertEqual(v.value, float("inf"))

    def test_rpow_v4(self):
        """"""
        try:
            v = float("inf") ** self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rpow_v5(self):
        """"""
        try:
            v = float("-inf") ** self.v5
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_rpow_v6(self):
        """"""
        try:
            v = float("-inf") ** self.v6
            check = False
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_lt(self):
        """"""
        v = self.v1 < self.v2
        v2 = self.v1 > self.v2
        self.assertTrue(v)
        self.assertFalse(v2)

    def test_le(self):
        """"""
        v = self.v2 <= self.v2
        v2 = self.v2 > self.v2
        self.assertTrue(v)
        self.assertFalse(v2)

    def test_gt(self):
        """"""
        v = self.v2 > self.v1
        v2 = self.v2 < self.v1
        self.assertTrue(v)
        self.assertFalse(v2)

    def test_ge(self):
        """"""
        v = self.v1 >= self.v1
        v2 = self.v1 < self.v1
        self.assertTrue(v)
        self.assertFalse(v2)

    def test_eq(self):
        """"""
        v = self.v1 == self.v1
        v2 = self.v2 == self.v1
        self.assertTrue(v)
        self.assertFalse(v2)

    def test_ne(self):
        """"""
        v = self.v2 != self.v1
        v2 = self.v2 == self.v1
        self.assertTrue(v)
        self.assertFalse(v2)


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


class NTupleValueTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = NTupleValue(v=tuple([NumericValue(1), NumericValue(2)]))
        self.v2 = NTupleValue(v=tuple([NumericValue(1), NumericValue(3)]))

    def test__len__(self):
        self.assertEqual(len(self.v1), 2)

    def test__add__(self):
        v3 = self.v1 + self.v2
        self.assertEqual(v3[0].value, 2)
        self.assertEqual(v3[1].value, 5)

    def test__sub__(self):
        v3 = self.v1 - self.v2
        self.assertEqual(v3[0].value, 0)
        self.assertEqual(v3[1].value, -1)

    def test__rsub__(self):
        v3 = 0 - self.v2
        self.assertEqual(v3[0].value, -1)
        self.assertEqual(v3[1].value, -3)

    def test__mul__(self):
        v3 = self.v1 * self.v2
        self.assertEqual(v3[0].value, 1)
        self.assertEqual(v3[1].value, 6)

    def test__truediv__(self):
        v3 = self.v2 / self.v1
        self.assertEqual(v3[0].value, 1)
        self.assertEqual(v3[1].value, 1.5)

    def test__floordiv__(self):
        v3 = self.v2 // self.v1
        self.assertEqual(v3[0].value, 1)
        self.assertEqual(v3[1].value, 1)

    def test__rtruediv__(self):
        v3 = 1 / self.v1
        self.assertEqual(v3[0].value, 1)
        self.assertEqual(v3[1].value, 0.5)

    def test__rfloordiv__(self):
        v3 = 1 // self.v1
        self.assertEqual(v3[0].value, 1)
        self.assertEqual(v3[1].value, 0)

    def test_is_numeric(self):
        """"""
        self.assertTrue(self.v1.is_numeric())

    def test_is_string(self):
        """"""
        self.assertFalse(self.v1.is_string())

    def test_is_container(self):
        """"""
        self.assertTrue(self.v1.is_container())

    def test_is_callable(self):
        """"""
        self.assertFalse(self.v1.is_callable())

    def test_instantiate(self):
        """"""
        try:
            v = NTupleValue(v=[StringValue("1"), StringValue("3")])
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


class IntervalPairTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = NumericInterval(
            lower=NumericValue(1), upper=NumericValue(2.3), open_on=IntervalConf.Upper
        )
        self.v2 = NumericInterval(
            lower=NumericValue(2.3), upper=NumericValue(2.4), open_on=None
        )
        self.p_1 = IntervalPair(lower=self.v1, upper=self.v2)

        self.v3 = NumericInterval(
            lower=NumericValue(2.4), upper=NumericValue(2.5), open_on=IntervalConf.Lower
        )
        self.v4 = NumericInterval(
            lower=NumericValue(2.5), upper=NumericValue(2.6), open_on=IntervalConf.Lower
        )
        self.p_2 = IntervalPair(lower=self.v3, upper=self.v4)

    def test_constructor(self):
        """"""
        val = IntervalPair(lower=self.v2, upper=self.v1)
        self.assertEqual(val._lower, self.v1)

    def test_or_v1_non_overlapping_result(self):
        """
        non overlapping interval case
        """
        breakpoint()
        pv = self.p_1 | NumericInterval(
            lower=NumericValue(2.4),
            upper=NumericValue(2.42),
            open_on=IntervalConf.Upper,
        )
        self.assertEqual(self.p_1._lower, pv._lower)

        print("upper",pv._upper)
        self.assertEqual(
            NumericInterval(
                lower=NumericValue(2.3),
                upper=NumericValue(2.42),
                open_on=IntervalConf.Upper,
            ),
            pv._upper,
        )

    def test_or_v2_overlapping_result(self):
        """"""
        pv = self.p_1 | NumericInterval(
            lower=NumericValue(1.4),
            upper=NumericValue(2.42),
            open_on=IntervalConf.Upper,
        )
        self.assertEqual(
            NumericInterval(
                lower=NumericValue(1),
                upper=NumericValue(2.42),
                open_on=IntervalConf.Upper,
            ),
            pv,
        )

    def test_or_v3_interval_pair_with_interval_result(self):
        """"""
        a = NumericInterval(
            lower=NumericValue(2.3),
            upper=NumericValue(2.42),
            open_on=IntervalConf.Lower,
        )
        pv = self.p_1 | a
        self.assertEqual(pv._lower, self.v1)
        self.assertEqual(
            pv._upper, NumericInterval(lower=a.lower, upper=a.upper, open_on=None)
        )

    def test_or_v4_2_interval_pair_result(self):
        """"""
        a = NumericInterval(
            lower=NumericValue(0.3),
            upper=NumericValue(1),
            open_on=IntervalConf.Upper,
        )
        pv = self.p_1 | a
        lower_pair = IntervalPair(lower=a, upper=self.p_1._lower)
        upper_pair = IntervalPair(lower=a, upper=self.p_1._upper)
        self.assertEqual(pv._lower, self.v1)
        self.assertEqual(
            pv._upper, NumericInterval(lower=a.lower, upper=a.upper, open_on=None)
        )


class NumericIntervalTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.v1 = NumericInterval(
            lower=NumericValue(1), upper=NumericValue(2.2), open_on=IntervalConf.Lower
        )
        self.v2 = NumericInterval(
            lower=NumericValue(0), upper=NumericValue(2), open_on=None
        )
        self.v3 = NumericInterval(
            lower=NumericValue(2.3), upper=NumericValue(2.4), open_on=None
        )
        self.v4 = NumericInterval(
            lower=NumericValue(2.2), upper=NumericValue(2.4), open_on=None
        )
        self.v5 = NumericInterval(
            lower=NumericValue(2.2), upper=NumericValue(2.4), open_on=IntervalConf.Lower
        )
        self.v6 = NumericInterval(
            lower=NumericValue(2.2), upper=NumericValue(2.4), open_on=IntervalConf.Upper
        )
        self.v7 = NumericInterval(
            lower=NumericValue(2.2), upper=NumericValue(2.4), open_on=IntervalConf.Both
        )

    def test_lt_v1(self):
        """"""
        self.assertTrue(self.v2 < self.v3)

    def test_lt_v2(self):
        """"""
        self.assertFalse(self.v1 < self.v4)

    def test_lt_v3(self):
        """"""
        self.assertTrue(self.v1 < self.v5)

    def test_lt_v4(self):
        """"""
        fs = self.v1 < frozenset([self.v5])
        self.assertTrue(fs)

    def test_lt_v5(self):
        """"""
        fs = self.v1 < frozenset([self.v5, self.v3])
        self.assertTrue(fs)

    def test_neq_v1(self):
        """"""
        f = self.v2 != self.v3
        self.assertTrue(f)

    def test_neq_v2(self):
        """"""
        f = self.v1 != self.v5
        self.assertTrue(f)

    def test_neq_v3(self):
        """"""
        fs = self.v1 != frozenset([self.v5])
        self.assertTrue(fs)

    def test_contains_v1(self):
        """"""
        self.assertFalse(NumericValue(2.2) in self.v5)

    def test_contains_v2(self):
        """"""
        self.assertTrue(NumericValue(2.2) in self.v4)

    def test_contains_v3(self):
        """"""
        self.assertFalse(NumericValue(2.4) in self.v6)

    def test_contains_v4(self):
        """"""
        self.assertFalse(NumericValue(2.4) in self.v7)

    def test_contains_v5(self):
        """"""
        self.assertTrue(NumericValue(2.3) in self.v7)

    def test_contains_v6(self):
        """"""
        self.assertTrue(NumericValue(2.3) in self.v6)

    def test_contains_v7(self):
        """"""
        self.assertTrue(NumericValue(2.3) in self.v5)

    def test_and_v1(self):
        """"""
        v_inter = self.v1 & self.v2
        self.assertEqual(
            v_inter,
            NumericInterval(
                lower=NumericValue(1), upper=NumericValue(2), open_on=IntervalConf.Lower
            ),
        )

    def test_and_v2(self):
        """"""
        v_i = self.v3 & self.v2
        self.assertEqual(v_i, frozenset())

    def test_and_v3(self):
        """"""
        v_i = self.v7 & self.v3
        self.assertEqual(
            v_i,
            NumericInterval(
                lower=NumericValue(2.3),
                upper=NumericValue(2.4),
                open_on=IntervalConf.Upper,
            ),
        )

    def test_and_v4(self):
        """"""
        v_i = self.v7 & self.v4
        self.assertEqual(
            v_i,
            self.v7,
        )

    def test_or_v1(self):
        """"""
        v_or = self.v1 | self.v2
        self.assertEqual(
            v_or,
            NumericInterval(
                lower=NumericValue(0), upper=NumericValue(2.2), open_on=None
            ),
        )

    def test_or_v2(self):
        """"""
        v_i = self.v3 | self.v2
        self.assertEqual(v_i, frozenset([self.v3, self.v2]))

    def test_or_v3(self):
        """"""
        v_i = self.v7 | self.v3
        self.assertEqual(
            v_i,
            NumericInterval(
                lower=NumericValue(2.2),
                upper=NumericValue(2.4),
                open_on=IntervalConf.Lower,
            ),
        )

    def test_or_v4(self):
        """"""
        v_i = self.v7 | self.v4
        self.assertEqual(
            v_i,
            self.v4,
        )

    def test_or_v5(self):
        """"""
        v_i = self.v7 | frozenset([self.v5, self.v6])
        self.assertEqual(v_i, frozenset([self.v5, self.v6]))

    def test_sub_v1(self):
        """"""
        v_i = self.v4 - self.v5
        self.assertEqual(
            v_i,
            NumericInterval(
                lower=NumericValue(2.2), upper=NumericValue(2.2), open_on=None
            ),
        )

    def test_sub_v2(self):
        """"""
        v_i = self.v2 - self.v3
        self.assertEqual(
            v_i,
            self.v2,
        )

    def test_sub_v3(self):
        """"""
        v_i = self.v5 - self.v3
        self.assertEqual(
            v_i,
            NumericInterval(
                lower=NumericValue(2.2),
                upper=NumericValue(2.3),
                open_on=IntervalConf.Both,
            ),
        )

    def test_sub_v4(self):
        """"""
        v_i = self.v4 - self.v3
        self.assertEqual(
            v_i,
            NumericInterval(
                lower=NumericValue(2.2),
                upper=NumericValue(2.3),
                open_on=IntervalConf.Upper,
            ),
        )

    def test_sub_v5(self):
        """"""
        v_i = self.v1 - self.v2
        self.assertEqual(
            v_i,
            NumericInterval(
                lower=NumericValue(2),
                upper=NumericValue(2.2),
                open_on=IntervalConf.Lower,
            ),
        )

    def test_invert_v1(self):
        """"""
        v_i = ~self.v1
        v_1 = ~v_i
        print("invert")
        print(str(v_i))
        print(str(v_1))
        print(str(self.v1))
        self.assertEqual(v_1, self.v1)


if __name__ == "__main__":
    unittest.main()
