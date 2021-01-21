"""!
test for factor.py
"""
from gmodels.factor import Factor
from gmodels.randomvariable import NumCatRVariable
from gmodels.gtypes.edge import Edge, EdgeType
import unittest
from random import choice


class TestFactor(unittest.TestCase):
    """!
    """

    def setUp(self):
        ""
        input_data = {
            "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
            "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
            "dice": {"outcome-values": [i for i in range(1, 7)], "evidence": 1.0 / 6},
            "fdice": {"outcome-values": [i for i in range(1, 7)]},
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

        def f_dice_dist(dice_value: float):
            if dice_value in [i for i in range(1, 5)]:
                return 0.2
            else:
                return 0.2

        # intelligence
        # grade
        self.intelligence = NumCatRVariable(
            node_id="int",
            input_data=input_data["intelligence"],
            distribution=intelligence_dist,
        )
        nid2 = "grade"
        self.grade = NumCatRVariable(
            node_id=nid2, input_data=input_data["grade"], distribution=grade_dist
        )
        nid3 = "dice"
        self.dice = NumCatRVariable(
            node_id=nid3, input_data=input_data["dice"], distribution=fair_dice_dist
        )
        nid4 = "fdice"
        self.fdice = NumCatRVariable(
            node_id=nid4, input_data=input_data["fdice"], distribution=f_dice_dist
        )
        self.f = Factor(
            gid="f", scope_vars=set([self.grade, self.dice, self.intelligence])
        )
        self.f2 = Factor(gid="f2", scope_vars=set([self.grade, self.fdice]))

    def test_id(self):
        ""
        self.assertEqual(self.f.id(), "f")

    def test_in_scope_t_num(self):
        self.assertTrue(self.f.in_scope(self.dice))

    def test_in_scope_t_str(self):
        self.assertTrue(self.f.in_scope(self.dice.id()))

    def test_in_scope_f_str(self):
        self.assertFalse(self.f.in_scope("fdsfdsa"))

    def test_scope_vars(self):
        self.assertTrue(
            self.f.scope_vars(), set([self.dice, self.intelligence, self.grade])
        )

    def test_marginal_joint(self):
        """
        """
        mjoint = self.f.marginal_joint(set([("int", 0.1), ("grade", 0.4), ("dice", 2)]))
        dmarg = self.dice.marginal(2)
        imarg = self.intelligence.marginal(0.1)
        gmarg = self.grade.marginal(0.4)
        self.assertTrue(mjoint, dmarg * imarg * gmarg)

    def test_partition_value(self):
        ""
        pval = self.f.partition_value()
        self.assertTrue(pval, 1.0)

    def test_phi(self):
        ""
        mjoint = self.f.phi(set([("int", 0.1), ("grade", 0.4), ("dice", 2)]))
        dmarg = self.dice.marginal(2)
        imarg = self.intelligence.marginal(0.1)
        gmarg = self.grade.marginal(0.4)
        self.assertTrue(mjoint, dmarg * imarg * gmarg)

    def test_phi_normalize(self):
        mjoint = self.f.phi(set([("int", 0.1), ("grade", 0.4), ("dice", 2)]))
        dmarg = self.dice.marginal(2)
        imarg = self.intelligence.marginal(0.1)
        gmarg = self.grade.marginal(0.4)
        self.assertTrue(mjoint, (dmarg * imarg * gmarg) / self.f.partition_value())

    def test_factor_product(self):
        ""
        f3 = self.f.product(self.f2)
