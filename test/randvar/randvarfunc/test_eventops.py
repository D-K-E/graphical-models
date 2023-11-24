"""
"""
import unittest

from pygmodels.randvar.randvarmodel.event import Event
from pygmodels.randvar.randvarfunc.eventops import EventBoolOps
from pygmodels.randvar.randvarfunc.eventops import EventEventOps
from pygmodels.randvar.randvarfunc.eventops import EventEventSetOps
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcome
from pygmodels.randvar.randvartype.baserandvar2 import BaseEvidence
from pygmodels.value.valuetype.value import NumericValue


class EventBoolOpsTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # dice random variable
        self.X = Event(
            randvar_id="X",
            randvar_name="CoinToss",
            outcomes=PossibleOutcomes(
                iterable=set(
                    [
                        PossibleOutcome(v=NumericValue(0), randvar_id="X"),
                        PossibleOutcome(v=NumericValue(1), randvar_id="X"),
                    ]
                ),
                name="coin-sides",
            ),
        )
        self.Y = Event(
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
            evidence=BaseEvidence(
                evidence_id="event_result",
                value=PossibleOutcome(v=NumericValue(0), randvar_id="Y"),
                randvar_id="Y",
            ),
        )
        self.Z = Event(
            randvar_id="Z",
            randvar_name="CoinToss",
            outcomes=PossibleOutcomes(
                iterable=set(
                    [
                        PossibleOutcome(v=NumericValue(0), randvar_id="Z"),
                        PossibleOutcome(v=NumericValue(1), randvar_id="Z"),
                    ]
                ),
                name="coin-sides",
            ),
            evidence=BaseEvidence(
                evidence_id="event_result",
                value=PossibleOutcome(v=NumericValue(1), randvar_id="Z"),
                randvar_id="Z",
            ),
        )

    def test_is_incompatible(self):
        """"""
        is_incompatible = EventBoolOps.is_incompatible(e=self.X, f=self.Y)
        self.assertTrue(is_incompatible)

    def test_is_exhaustive(self):
        """"""
        is_exhaustive = EventBoolOps.is_exhaustive(es=[self.X, self.Z])
        self.assertTrue(is_exhaustive)

    def test_is_partition(self):
        """"""
        is_partition = EventBoolOps.is_partition(es=[self.X, ~self.X])
        self.assertTrue(is_partition)

    def test_is_subset_of(self):
        """"""
        is_subset = EventBoolOps.is_subset_of(e=self.Y, f=self.Z)
        self.assertTrue(is_subset)


class EventEventOpsTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # dice random variable
        self.X = Event(
            randvar_id="X",
            randvar_name="CoinToss",
            outcomes=PossibleOutcomes(
                iterable=set(
                    [
                        PossibleOutcome(v=NumericValue(0), randvar_id="X"),
                        PossibleOutcome(v=NumericValue(1), randvar_id="X"),
                    ]
                ),
                name="coin-sides",
            ),
        )
        self.Y = Event(
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
            evidence=BaseEvidence(
                evidence_id="event_result",
                value=PossibleOutcome(v=NumericValue(0), randvar_id="Y"),
                randvar_id="Y",
            ),
        )
        self.Z = Event(
            randvar_id="Z",
            randvar_name="CoinToss",
            outcomes=PossibleOutcomes(
                iterable=set(
                    [
                        PossibleOutcome(v=NumericValue(0), randvar_id="Z"),
                        PossibleOutcome(v=NumericValue(1), randvar_id="Z"),
                    ]
                ),
                name="coin-sides",
            ),
            evidence=BaseEvidence(
                evidence_id="event_result",
                value=PossibleOutcome(v=NumericValue(1), randvar_id="Z"),
                randvar_id="Z",
            ),
        )

    def test_logical_sum(self):
        """"""
        XY = EventEventOps.logical_sum(e=self.X, f=self.Y)
        self.assertEqual(XY, self.X)

    def test_partition_from_event(self):
        """"""
        e, e_inv = EventEventOps.partition_from_event(e=self.Y)
        self.assertEqual(e, self.Y)
        self.assertEqual(e_inv, self.Z)
        self.assertTrue(EventBoolOps.is_partition([e, e_inv]))

    def test_logical_sum(self):
        "Biagini, Campanino, 2016, p. 5"
        xz = self.X | self.Z
        compare = (self.X + self.Z) - (self.X * self.Z)
        self.assertEqual(xz, compare)

    def test_logical_product(self):
        "Biagini, Campanino, 2016, p. 5"
        xz = self.X & self.Z
        compare = self.X * self.Z
        self.assertEqual(xz, compare)


if __name__ == "__main__":
    unittest.main()
