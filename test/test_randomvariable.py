# unittest for numeric categorical random variable


import unittest
from gmodels.randomvariable import NumCatRVariable
import math


class NumCatRVariableTest(unittest.TestCase):
    def setUp(self):
        nid1 = "rvar1"
        input_data = {
            "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
            "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
            "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
        }

        def intelligence_dist(intelligence_value: float):
            if intelligence_value == 0.1:
                return 0.7
            elif intelligence_value == 0.9:
                return 0.3
            else:
                return 0

        def grade_dist(grade_value: float):
            if grade_value == 0.2:
                return 0.25
            elif grade_value == 0.4:
                return 0.37
            elif grade_value == 0.6:
                return 0.38
            else:
                return 0

        def fair_dice_dist(dice_value: float):
            if dice_value in [i for i in range(1, 7)]:
                return 1.0 / 6.0
            else:
                return 0

        # intelligence
        # grade
        self.intelligence = NumCatRVariable(
            node_id=nid1,
            input_data=input_data["intelligence"],
            distribution=intelligence_dist,
        )
        nid2 = "rvar2"
        self.grade = NumCatRVariable(
            node_id=nid2, input_data=input_data["grade"], distribution=grade_dist
        )
        nid3 = "rvar3"
        self.dice = NumCatRVariable(
            node_id=nid3, input_data=input_data["dice"], distribution=fair_dice_dist
        )

    def test_id(self):
        ""
        self.assertEqual(self.grade.id(), "rvar2")

    def test_expected_value(self):
        ""
        self.assertEqual(self.dice.expected_value(), 3.5)

    def test_marginal_with_known_value(self):
        ""
        self.assertEqual(self.grade.marginal(0.4), 0.37)

    def test_marginal_with_unknown_value(self):
        ""
        self.assertEqual(self.grade.marginal(0.8), 0.0)

    def test_P_X(self):
        ""
        self.assertEqual(self.dice.P_X(), 3.5)

    def test_p_x_known_value(self):
        ""
        self.assertEqual(self.grade.p_x(0.4), 0.37)

    def test_p_x_unknown_value(self):
        ""
        self.assertEqual(self.grade.p_x(0.8), 0.0)

    def test_marginal_over(self):
        ""
        eval_value = 0.2
        margover = self.grade.marginal_over(eval_value, self.dice)
        self.assertEqual(margover, 3.5 * 0.25)

    def test_marginal_over_evidence_key(self):
        ""
        margover = self.grade.marginal_over_evidence_key(self.dice)
        self.assertEqual(margover, 3.5 * 0.25)

    def test_joint_without_evidence(self):
        dice = self.dice
        dice.pop_evidence()
        self.assertEqual(dice.joint(dice), 3.5 * 3.5)

    def test_variance(self):
        self.assertEqual(round(self.dice.variance(), 3), 2.917)

    def test_standard_deviation(self):
        ""
        self.assertEqual(
            round(self.dice.standard_deviation(), 3), round(math.sqrt(2.917), 3)
        )


if __name__ == "__main__":
    unittest.main()
