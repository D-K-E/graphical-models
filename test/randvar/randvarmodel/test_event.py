"""
"""
import unittest

from pygmodels.randvar.randvarmodel.event import Event
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcome
from pygmodels.randvar.randvartype.baserandvar2 import BaseEvidence
from pygmodels.value.valuetype.value import NumericValue


class EventTest(unittest.TestCase):
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
        #
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

    def test_constructor(self):
        """"""
        check = False
        try:
            Event(
                randvar_id="Z",
                randvar_name="CoinTossV",
                outcomes=PossibleOutcomes(
                    iterable=set(
                        [
                            PossibleOutcome(v=NumericValue(1), randvar_id="Z"),
                            PossibleOutcome(v=NumericValue(1.1), randvar_id="Z"),
                        ]
                    ),
                    name="coin-sides",
                ),
            )
        except ValueError:
            check = True
        self.assertEqual(check, True)


if __name__ == "__main__":
    unittest.main()
