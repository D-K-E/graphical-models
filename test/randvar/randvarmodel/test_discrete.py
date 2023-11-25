"""
\brief tests about discrete.py
"""
import math
import unittest

from pygmodels.randvar.randvarmodel.discrete import (
    DiscreteRandomNumber,
)
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcome
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.domain import DomainValue
from pygmodels.value.valuetype.value import NumericValue


class DiscreteRandomNumberTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # dice random variable
        self.X = DiscreteRandomNumber(
            randvar_id="X",
            randvar_name="DiceRoll",
            outcomes=PossibleOutcomes(
                iterable=set(
                    [
                        PossibleOutcome(v=NumericValue(0), randvar_id="X"),
                        PossibleOutcome(v=NumericValue(1), randvar_id="X"),
                        PossibleOutcome(v=NumericValue(2), randvar_id="X"),
                        PossibleOutcome(v=NumericValue(3), randvar_id="X"),
                        PossibleOutcome(v=NumericValue(4), randvar_id="X"),
                        PossibleOutcome(v=NumericValue(5), randvar_id="X"),
                    ]
                ),
                name="dice-sides",
            ),
        )
        #
        self.Y = DiscreteRandomNumber(
            randvar_id="Y",
            randvar_name="CoinToss",
            outcomes=PossibleOutcomes(
                iterable=set(
                    [
                        PossibleOutcome(v=NumericValue(0), randvar_id="Y"),
                        PossibleOutcome(v=NumericValue(1), randvar_id="Y"),
                    ]
                ),
                name="coin-sides",
            ),
        )
        self.A = DiscreteRandomNumber(
            randvar_id="A",
            randvar_name="CoinToss_Variant",
            outcomes=PossibleOutcomes(
                iterable=set(
                    [
                        PossibleOutcome(v=NumericValue(1), randvar_id="A"),
                        PossibleOutcome(v=NumericValue(2), randvar_id="A"),
                    ]
                ),
                name="coin-sides",
            ),
        )

    def test_upper_bound(self):
        """"""
        self.assertEqual(self.X.upper_bound, 5)

    def test_lower_bound(self):
        """"""
        self.assertEqual(self.X.lower_bound, 0)

    def test_is_upper_bounded(self):
        """"""
        self.assertEqual(self.X.is_upper_bounded(), True)

    def test_is_lower_bounded(self):
        """"""
        self.assertEqual(self.X.is_lower_bounded(), True)

    def test_is_bounded(self):
        """"""
        self.assertEqual(self.X.is_bounded(), True)

    def test_and(self):
        """"""
        Z = self.X & self.Y
        outs = set()
        for z in Z:
            outs.add(z.value)
        self.assertEqual(outs, {0, 1})

    def test_or(self):
        """"""
        Z = self.X | self.Y
        fouts = set()
        for z in Z:
            fouts.add(z.value)
        self.assertEqual(fouts, {0, 1, 2, 3, 4, 5})

    def test_invert(self):
        """"""
        Z = ~self.Y
        fouts = set()
        for z in Z:
            fouts.add(z.value)
        self.assertEqual(fouts, {0, 1})

    def test_add(self):
        """"""
        Z = self.X + self.Y
        outs = set()
        for z in Z:
            outs.add(z.value)
        self.assertEqual(outs, set([0, 1, 2, 3, 4, 5, 6]))

    def test_sub(self):
        """"""
        Z = self.X - self.Y
        outs = set()
        for z in Z:
            outs.add(z.value)
        self.assertEqual(outs, set([-1, 0, 1, 2, 3, 4, 5]))

    def test_mul(self):
        """"""
        Z = self.X * self.Y
        outs = set()
        for z in Z:
            outs.add(z.value)
        self.assertEqual(outs, set([0, 1, 2, 3, 4, 5]))

    def test_truediv(self):
        """"""
        Z = self.Y / self.A
        outs = set()
        for z in Z:
            outs.add(z.value)
        self.assertEqual(outs, set([0, 0.5, 1]))

    def test_outcomes(self):
        """"""
        comp = PossibleOutcomes(
            iterable=(
                i
                for i in [
                    PossibleOutcome(v=NumericValue(0), randvar_id="Y"),
                    PossibleOutcome(v=NumericValue(1), randvar_id="Y"),
                ]
            ),
            name="coin-sides",
        )
        yout = self.Y.outcomes
        deep_comp = comp.deep_eq(yout)
        # deep comparison
        self.assertEqual(deep_comp, True)

        # shallow comparison
        self.assertEqual(yout, comp)


if __name__ == "__main__":
    unittest.main()