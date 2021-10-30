# unittest for numeric categorical random variable


import math
import unittest

from pygmodels.pgmtype.randomvariable import (
    CatRandomVariable,
    NumCatRVariable,
    PossibleOutcomes,
)


class NumCatRVariableTest(unittest.TestCase):
    def setUp(self):
        nid1 = "rvar1"
        input_data = {
            "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
            "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
            "dice": {
                "outcome-values": [i for i in range(1, 7)],
                "evidence": 1.0 / 6,
            },
        }

        def intelligence_dist(intelligence_value: float):
            if intelligence_value == 0.1:
                return 0.7
            elif intelligence_value == 0.9:
                return 0.3
            else:
                raise ValueError(
                    "intelligence_value does not belong to possible outcomes"
                )

        def grade_dist(grade_value: float):
            if grade_value == 0.2:
                return 0.25
            elif grade_value == 0.4:
                return 0.37
            elif grade_value == 0.6:
                return 0.38
            else:
                raise ValueError("unknown grade value")

        def fair_dice_dist(dice_value: float):
            if dice_value in [i for i in range(1, 7)]:
                return 1.0 / 6.0
            else:
                raise ValueError("dice value")

        # intelligence
        # grade
        self.intelligence = NumCatRVariable(
            node_id=nid1,
            input_data=input_data["intelligence"],
            marginal_distribution=intelligence_dist,
        )
        nid2 = "rvar2"
        self.grade = NumCatRVariable(
            node_id=nid2,
            input_data=input_data["grade"],
            marginal_distribution=grade_dist,
        )
        nid3 = "rvar3"
        self.dice = NumCatRVariable(
            node_id=nid3,
            input_data=input_data["dice"],
            marginal_distribution=fair_dice_dist,
        )
        #
        students = PossibleOutcomes(frozenset(["student_1", "student_2"]))

        def grade_f(x):
            return "F" if x == "student_1" else "A"

        def grade_distribution(x):
            return 0.1 if x == "F" else 0.9

        indata = {"possible-outcomes": students}
        self.rvar = CatRandomVariable(
            input_data=indata,
            node_id="myrandomvar",
            f=grade_f,
            marginal_distribution=grade_distribution,
        )

    def test_id(self):
        """"""
        self.assertEqual(self.grade.id(), "rvar2")

    def test_values(self):
        self.assertEqual(self.rvar.values(), frozenset(["A", "F"]))

    def test_value_set(self):
        self.assertEqual(
            self.rvar.value_set(
                value_transform=lambda x: x.lower(),
                value_filter=lambda x: x != "A",
            ),
            frozenset([("myrandomvar", "f")]),
        )

    def test_max_marginal_value(self):
        self.assertEqual(self.intelligence.max_marginal_value(), 0.1)

    def test_max(self):
        self.assertEqual(self.intelligence.max(), 0.7)

    def test_min(self):
        self.assertEqual(self.intelligence.min(), 0.3)

    def test_min_marginal_value(self):
        self.assertEqual(self.intelligence.min_marginal_value(), 0.9)

    def test_expected_value(self):
        """"""
        self.assertEqual(self.dice.expected_value(), 3.5)

    def test_marginal_with_known_value(self):
        """"""
        self.assertEqual(self.grade.marginal(0.4), 0.37)

    def test_p_x_known_value(self):
        """"""
        self.assertEqual(self.grade.p(0.4), 0.37)

    def test_P_X_e(self):
        """"""
        self.assertEqual(self.grade.P_X_e(), 0.25)

    def test_max_marginal_e(self):
        """"""
        self.assertEqual(self.grade.max_marginal_e(), 0.25)

    def test_min_marginal_e(self):
        """"""
        self.assertEqual(self.grade.min_marginal_e(), 0.25)

    def test_marginal_over(self):
        """"""
        eval_value = 0.2
        margover = self.grade.marginal_over(eval_value, self.dice)
        self.assertEqual(margover, 3.5 * 0.25)

    def test_marginal_over_evidence_key(self):
        """"""
        margover = self.grade.marginal_over_evidence_key(self.dice)
        self.assertEqual(margover, 3.5 * 0.25)

    def test_joint_without_evidence(self):
        dice = self.dice
        dice.pop_evidence()
        self.assertEqual(dice.joint(dice), 3.5 * 3.5)

    def test_variance(self):
        self.assertEqual(round(self.dice.variance(), 3), 2.917)

    def test_standard_deviation(self):
        """"""
        self.assertEqual(
            round(self.dice.standard_deviation(), 3),
            round(math.sqrt(2.917), 3),
        )


if __name__ == "__main__":
    unittest.main()
