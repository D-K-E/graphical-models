"""
\brief tests about discrete.py
"""
import math
import unittest

from pygmodels.randvar.randvarmodel.discrete import (
    DiscreteRandomNumber,
)
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.domain import DomainValue
from pygmodels.value.valuetype.value import NumericValue


class DiscreteRandomNumberTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # dice random variable
        svar_dname = "student"
        svar_id = "student01"
        self.X = DiscreteRandomNumber(
            randvar_id="X",
            randvar_name="X",
            outcomes=PossibleOutcomes(
                set(
                    [
                        CodomainValue(v=NumericValue(1), set_id="1", mapping_name="X"),
                        CodomainValue(v=NumericValue(2), set_id="2", mapping_name="X"),
                        CodomainValue(v=NumericValue(3), set_id="3", mapping_name="X"),
                        CodomainValue(v=NumericValue(4), set_id="4", mapping_name="X"),
                        CodomainValue(v=NumericValue(5), set_id="5", mapping_name="X"),
                        CodomainValue(v=NumericValue(6), set_id="6", mapping_name="X"),
                    ]
                )
            ),
        )
        #

    def test_upper_bound(self):
        """"""
        self.assertEqual(self.X.upper_bound, 6)

    def test_lower_bound(self):
        """"""
        self.assertEqual(self.X.lower_bound, 1)

    def test_lower_bound(self):
        """"""
        self.assertEqual(self.X.lower_bound, 1)

    def test_is_upper_bounded(self):
        """"""
        self.assertEqual(self.X.is_upper_bounded(), True)

    def test_is_lower_bounded(self):
        """"""
        self.assertEqual(self.X.is_lower_bounded(), True)

    def test_is_bounded(self):
        """"""
        self.assertEqual(self.X.is_bounded(), True)


if __name__ == "__main__":
    unittest.main()
