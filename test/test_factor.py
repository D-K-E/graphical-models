"""!
test for factor.py
"""
import math
import unittest
from random import choice

from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.factor.factor import Factor
from pygmodels.pgmtype.randomvariable import NumCatRVariable


class TestFactor(unittest.TestCase):
    """!"""

    def data_1(self):
        """"""
        input_data = {
            "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
            "grade": {"outcome-values": [0.2, 0.4, 0.6], "evidence": 0.2},
            "dice": {
                "outcome-values": [i for i in range(1, 7)],
                "evidence": 1.0 / 6,
            },
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
            marginal_distribution=intelligence_dist,
        )
        nid2 = "grade"
        self.grade = NumCatRVariable(
            node_id=nid2,
            input_data=input_data["grade"],
            marginal_distribution=grade_dist,
        )
        nid3 = "dice"
        self.dice = NumCatRVariable(
            node_id=nid3,
            input_data=input_data["dice"],
            marginal_distribution=fair_dice_dist,
        )
        nid4 = "fdice"
        self.fdice = NumCatRVariable(
            node_id=nid4,
            input_data=input_data["fdice"],
            marginal_distribution=f_dice_dist,
        )
        self.f = Factor(
            gid="f", scope_vars=set([self.grade, self.dice, self.intelligence])
        )
        self.f2 = Factor(gid="f2", scope_vars=set([self.grade, self.fdice]))

    def data_2(self):
        """"""
        # Koller, Friedman 2009, p. 104
        self.Af = NumCatRVariable(
            node_id="A",
            input_data={"outcome-values": [10, 50]},
            marginal_distribution=lambda x: 0.5,
        )
        self.Bf = NumCatRVariable(
            node_id="B",
            input_data={"outcome-values": [10, 50]},
            marginal_distribution=lambda x: 0.5,
        )
        self.Cf = NumCatRVariable(
            node_id="C",
            input_data={"outcome-values": [10, 50]},
            marginal_distribution=lambda x: 0.5,
        )
        self.Df = NumCatRVariable(
            node_id="D",
            input_data={"outcome-values": [10, 50]},
            marginal_distribution=lambda x: 0.5,
        )

        def phiAB(scope_product):
            """"""
            sfs = set(scope_product)
            if sfs == set([("A", 10), ("B", 10)]):
                return 30
            elif sfs == set([("A", 10), ("B", 50)]):
                return 5
            elif sfs == set([("A", 50), ("B", 10)]):
                return 1
            elif sfs == set([("A", 50), ("B", 50)]):
                return 10
            else:
                raise ValueError("unknown arg")

        self.AB = Factor(
            gid="AB", scope_vars=set([self.Af, self.Bf]), factor_fn=phiAB
        )

        def phiBC(scope_product):
            """"""
            sfs = set(scope_product)
            if sfs == set([("B", 10), ("C", 10)]):
                return 100
            elif sfs == set([("B", 10), ("C", 50)]):
                return 1
            elif sfs == set([("B", 50), ("C", 10)]):
                return 1
            elif sfs == set([("B", 50), ("C", 50)]):
                return 100
            else:
                raise ValueError("unknown arg")

        self.BC = Factor(
            gid="BC", scope_vars=set([self.Bf, self.Cf]), factor_fn=phiBC
        )

    def data_3(self):
        """"""

        def phiCD(scope_product):
            """"""
            sfs = set(scope_product)
            if sfs == set([("C", 10), ("D", 10)]):
                return 1
            elif sfs == set([("C", 10), ("D", 50)]):
                return 100
            elif sfs == set([("C", 50), ("D", 10)]):
                return 100
            elif sfs == set([("C", 50), ("D", 50)]):
                return 1
            else:
                raise ValueError("unknown arg")

        self.CD = Factor(
            gid="CD", scope_vars=set([self.Cf, self.Df]), factor_fn=phiCD
        )

        def phiDA(scope_product):
            """"""
            sfs = set(scope_product)
            if sfs == set([("D", 10), ("A", 10)]):
                return 100
            elif sfs == set([("D", 10), ("A", 50)]):
                return 1
            elif sfs == set([("D", 50), ("A", 10)]):
                return 1
            elif sfs == set([("D", 50), ("A", 50)]):
                return 100
            else:
                raise ValueError("unknown arg")

        self.DA = Factor(
            gid="DA", scope_vars=set([self.Df, self.Af]), factor_fn=phiDA
        )

    def setUp(self):
        """"""
        self.data_1()
        self.data_2()
        self.data_3()

        # Koller, Friedman 2009 p. 107
        self.af = NumCatRVariable(
            node_id="A",
            input_data={"outcome-values": [10, 50, 20]},
            marginal_distribution=lambda x: 0.4 if x != 20 else 0.2,
        )

        def phiaB(scope_product):
            """"""
            sfs = set(scope_product)
            if sfs == set([("A", 10), ("B", 10)]):
                return 0.5
            elif sfs == set([("A", 10), ("B", 50)]):
                return 0.8
            elif sfs == set([("A", 50), ("B", 10)]):
                return 0.1
            elif sfs == set([("A", 50), ("B", 50)]):
                return 0
            elif sfs == set([("A", 20), ("B", 10)]):
                return 0.3
            elif sfs == set([("A", 20), ("B", 50)]):
                return 0.9
            else:
                raise ValueError("unknown arg")

        self.aB = Factor(
            gid="ab", scope_vars=set([self.af, self.Bf]), factor_fn=phiaB
        )

        def phibc(scope_product):
            """"""
            sfs = set(scope_product)
            if sfs == set([("B", 10), ("C", 10)]):
                return 0.5
            elif sfs == set([("B", 10), ("C", 50)]):
                return 0.7
            elif sfs == set([("B", 50), ("C", 10)]):
                return 0.1
            elif sfs == set([("B", 50), ("C", 50)]):
                return 0.2
            else:
                raise ValueError("unknown arg")

        self.bc = Factor(
            gid="bc", scope_vars=set([self.Bf, self.Cf]), factor_fn=phibc
        )

    def test_id(self):
        """"""
        self.assertEqual(self.f.id(), "f")

    def test_domain_scope(self):
        """"""
        d = self.AB.domain_scope(
            domain=[set([("A", 50), ("B", 50)]), set([("A", 10), ("B", 10)])]
        )
        self.assertEqual(set(d), set([self.Af, self.Bf]))

    def test_has_var(self):
        """"""
        intuple = self.f.has_var(ids="dice")
        nottuple = self.f.has_var(ids="dice22")
        self.assertTrue(intuple[0])
        self.assertEqual(intuple[1], self.dice)
        self.assertFalse(nottuple[0])
        self.assertEqual(nottuple[1], None)

    def test_in_scope_t_num(self):
        self.assertTrue(self.dice in self.f)

    def test_in_scope_t_str(self):
        self.assertTrue(self.dice.id() in self.f)

    def test_in_scope_f_str(self):
        self.assertFalse("fdsfdsa" in self.f)

    def test_scope_vars(self):
        self.assertTrue(
            self.f.scope_vars(),
            set([self.dice, self.intelligence, self.grade]),
        )

    def test_marginal_joint(self):
        """ """
        mjoint = self.f.marginal_joint(
            set([("int", 0.1), ("grade", 0.4), ("dice", 2)])
        )
        dmarg = self.dice.marginal(2)
        imarg = self.intelligence.marginal(0.1)
        gmarg = self.grade.marginal(0.4)
        self.assertTrue(mjoint, dmarg * imarg * gmarg)

    def test_partition_value(self):
        """"""
        pval = self.f.partition_value(self.f.vars_domain())
        self.assertTrue(pval, 1.0)

    def test_phi(self):
        """"""
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
        self.assertTrue(mjoint, (dmarg * imarg * gmarg) / self.f.zval())

    def test_from_scope_variables_with_fn(self):
        """"""
        A = NumCatRVariable(
            "A",
            input_data={"outcome-values": [True, False]},
            marginal_distribution=lambda x: 0.6 if x else 0.4,
        )
        B = NumCatRVariable(
            "B",
            input_data={"outcome-values": [True, False]},
            marginal_distribution=lambda x: 0.62 if x else 0.38,
        )

        def phi_ab(scope_product):
            ss = set(scope_product)
            if ss == set([("A", True), ("B", True)]):
                return 0.9
            elif ss == set([("A", True), ("B", False)]):
                return 0.1
            elif ss == set([("A", False), ("B", True)]):
                return 0.2
            elif ss == set([("A", False), ("B", False)]):
                return 0.8
            else:
                raise ValueError("unknown argument")

        f = Factor.from_scope_variables_with_fn(svars=set([A, B]), fn=phi_ab)
        query = set([("A", True), ("B", True)])
        ff = f.phi(query)
        self.assertEqual(round(ff, 2), 0.9)

    @unittest.skip("Factor.from_conditional_vars not yet implemented")
    def test_from_conditional_vars(self):
        """"""
        # A = NumCatRVariable(
        #     "A",
        #     input_data={"outcome-values": [True, False]},
        #     marginal_distribution=lambda x: 0.6 if x else 0.4,
        # )
        # B = NumCatRVariable(
        #     "B",
        #     input_data={"outcome-values": [True, False]},
        #     marginal_distribution=lambda x: 0.62 if x else 0.38,
        # )

        def phi_ab(scope_product):
            ss = set(scope_product)
            if ss == set([("A", True), ("B", True)]):
                return 0.9
            elif ss == set([("A", True), ("B", False)]):
                return 0.1
            elif ss == set([("A", False), ("B", True)]):
                return 0.2
            elif ss == set([("A", False), ("B", False)]):
                return 0.8
            else:
                raise ValueError("unknown argument")

        # f = Factor.from_conditional_vars(X_i=B, Pa_Xi=set([A]))
        # query = set([("A", True), ("B", True)])
        # ff = f.phi(query)
        # self.assertEqual(round(ff, 2), 0.9)


if __name__ == "__main__":
    unittest.main()
