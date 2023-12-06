"""
\brief tests related to setops.py
"""

import unittest
from pygmodels.value.valuefunc.setops import SetBoolOps
from pygmodels.value.valuefunc.setops import SetSetOps
from pygmodels.value.valuetype.value import SetValue
from pygmodels.value.valuetype.value import StringValue
from pygmodels.value.valuetype.value import NumericIntervalValue
from pygmodels.value.valuetype.value import R
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.value.valuetype.abstractvalue import IntervalConf


class SetBoolOpsTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.coin = frozenset(
            [
                SetValue(v=StringValue("heads"), set_id="coin"),
                SetValue(v=StringValue("tails"), set_id="coin"),
            ]
        )
        self.R = R()

    def test_is_sigma_field_v1(self):
        """
        Checking the trivial sigma field as per, Shao 2010, p. 2
        """
        field = frozenset([frozenset(), self.coin])
        sample_space = self.coin
        is_sigma = SetBoolOps.is_sigma_field(iterable=field, sample_space=sample_space)
        self.assertTrue(is_sigma)

    def test_is_sigma_field_v2(self):
        """
        Checking the trivial sigma field as per, Shao 2010, p. 2
        """
        field = frozenset([frozenset()])
        sample_space = self.coin
        is_sigma = SetBoolOps.is_sigma_field(iterable=field, sample_space=sample_space)
        self.assertFalse(is_sigma)

    def test_is_sigma_field_v3(self):
        """
        Checking the trivial sigma field as per, Shao 2010, p. 2
        """
        field = frozenset([self.coin])
        sample_space = self.coin
        is_sigma = SetBoolOps.is_sigma_field(iterable=field, sample_space=sample_space)
        self.assertFalse(is_sigma)

    def test_is_sigma_field_v4(self):
        """
        Checking the gross sigma field as per, Shao 2010, p. 2
        """
        field = frozenset([frozenset(s) for s in SetSetOps.mk_powerset(self.coin)])
        sample_space = self.coin
        is_sigma = SetBoolOps.is_sigma_field(iterable=field, sample_space=sample_space)
        self.assertTrue(is_sigma)

    def test_is_sigma_field_v5(self):
        """
        Checking the trivial sigma field with real as per, Shao 2010, p. 2
        """
        field = frozenset([frozenset(), self.R])
        sample_space = self.R
        is_sigma = SetBoolOps.is_sigma_field(iterable=field, sample_space=sample_space)
        self.assertTrue(is_sigma)

    def test_is_sigma_field_v6(self):
        """
        Checking the gross sigma field as per, Shao 2010, p. 2
        """
        field = frozenset([frozenset(), self.R])
        sample_space = self.R
        is_sigma = SetBoolOps.is_sigma_field(iterable=field, sample_space=sample_space)
        self.assertTrue(is_sigma)


class SetSetOpsTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.heads = SetValue(v=StringValue("heads"), set_id="coin")
        self.tails = SetValue(v=StringValue("tails"), set_id="coin")
        self.coin = frozenset(
            [
                SetValue(v=StringValue("heads"), set_id="coin"),
                SetValue(v=StringValue("tails"), set_id="coin"),
            ]
        )
        self.R = R()
        self.v2 = NumericIntervalValue(
            lower=NumericValue(0), upper=NumericValue(2), open_on=None
        )

        self.v4 = NumericIntervalValue(
            lower=NumericValue(2.2), upper=NumericValue(2.4), open_on=None
        )
        self.v5 = NumericIntervalValue(
            lower=NumericValue(2.2), upper=NumericValue(2.4), open_on=IntervalConf.Lower
        )
        self.v6 = NumericIntervalValue(
            lower=NumericValue(2.2), upper=NumericValue(2.4), open_on=IntervalConf.Upper
        )
        self.v7 = NumericIntervalValue(
            lower=NumericValue(2.2), upper=NumericValue(2.4), open_on=IntervalConf.Both
        )

    def test_mk_trivial_sigma_field_v1(self):
        """"""
        field = SetSetOps.mk_trivial_sigma_field(sample_space=self.coin)
        is_field = SetBoolOps.is_sigma_field(field, sample_space=self.coin)
        self.assertTrue(is_field)

    def test_mk_trivial_sigma_field_v2(self):
        """"""
        field = SetSetOps.mk_trivial_sigma_field(sample_space=self.R)
        is_field = SetBoolOps.is_sigma_field(field, sample_space=self.R)
        self.assertTrue(is_field)

    def test_mk_sigma_field_from_subset_v1(self):
        """"""
        field = SetSetOps.mk_sigma_field_from_subset(
            sample_space=self.R, subset=self.v4
        )
        is_field = SetBoolOps.is_sigma_field(field, sample_space=self.R)
        self.assertTrue(is_field)

    def test_mk_sigma_field_from_subset_v2(self):
        """"""
        field = SetSetOps.mk_sigma_field_from_subset(
            sample_space=self.R, subset=frozenset([self.v4, self.v2])
        )
        is_field = SetBoolOps.is_sigma_field(field, sample_space=self.R)
        self.assertTrue(is_field)

    def test_mk_sigma_field_from_subset_v3(self):
        """"""
        field = SetSetOps.mk_sigma_field_from_subset(
            sample_space=self.coin, subset=frozenset([self.heads])
        )
        is_field = SetBoolOps.is_sigma_field(field, sample_space=self.coin)
        self.assertTrue(is_field)


if __name__ == "__main__":
    unittest.main()
