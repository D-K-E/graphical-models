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
                        PossibleOutcome(v=NumericValue(0), randvar_id="Y"),
                        PossibleOutcome(v=NumericValue(1), randvar_id="Y"),
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

    def test_is_incompatible(self):
        """"""
        is_incompatible = EventBoolOps.is_incompatible(e=self.X, f=self.Y)
        self.assertTrue(is_incompatible)


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
                        PossibleOutcome(v=NumericValue(0), randvar_id="Y"),
                        PossibleOutcome(v=NumericValue(1), randvar_id="Y"),
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

    def test_logical_sum(self):
        """"""
        XY = EventEventOps.logical_sum(e=self.X, f=self.Y)
        self.assertEqual(XY, self.X)


if __name__ == "__main__":
    unittest.main()
