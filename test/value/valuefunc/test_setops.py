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
        Checking the gross sigma field as per, Shao 2010, p. 2
        """
        field = frozenset([frozenset(), self.R])
        sample_space = self.R
        is_sigma = SetBoolOps.is_sigma_field(iterable=field, sample_space=sample_space)
        self.assertTrue(is_sigma)


if __name__ == "__main__":
    unittest.main()
