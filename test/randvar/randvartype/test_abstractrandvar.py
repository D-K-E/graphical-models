"""
"""
import unittest
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes


class PossibleOutcomesTest:
    def setUp(self):
        """"""
        self.i = PossibleOutcomes(
            iterable=set(
                [
                    CodomainValue(v=NumericValue(0), set_id="H", mapping_name="Y"),
                    CodomainValue(v=NumericValue(1), set_id="T", mapping_name="Y"),
                ]
            ),
            name="coin-sides",
        )
        self.j = PossibleOutcomes(
            iterable=set(
                [
                    CodomainValue(v=NumericValue(1), set_id="H", mapping_name="A"),
                    CodomainValue(v=NumericValue(2), set_id="T", mapping_name="A"),
                ]
            ),
            name="coin-sides",
        )

    def test_eq(self):
        """"""
        eq = self.i == self.j
        self.assertEqual(eq, True)

    def test_deep_eq(self):
        """"""
        eq = self.i.deep_eq(self.j)
        self.assertEqual(eq, False)
