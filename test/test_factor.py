"""!
test for factor.py
"""
from gmodels.factor import Factor
from gmodels.randomvariable import NumCatRVariable
from gmodels.gtypes.edge import Edge, EdgeType
import unittest
from random import choice
import math


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

        # Koller, Friedman 2009, p. 104
        self.Af = NumCatRVariable(
            node_id="A",
            input_data={"outcome-values": [10, 50]},
            distribution=lambda x: 0.5,
        )
        self.Bf = NumCatRVariable(
            node_id="B",
            input_data={"outcome-values": [10, 50]},
            distribution=lambda x: 0.5,
        )
        self.Cf = NumCatRVariable(
            node_id="C",
            input_data={"outcome-values": [10, 50]},
            distribution=lambda x: 0.5,
        )
        self.Df = NumCatRVariable(
            node_id="D",
            input_data={"outcome-values": [10, 50]},
            distribution=lambda x: 0.5,
        )

        def phiAB(scope_product):
            ""
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

        self.AB = Factor(gid="AB", scope_vars=set([self.Af, self.Bf]), factor_fn=phiAB)

        def phiBC(scope_product):
            ""
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

        self.BC = Factor(gid="BC", scope_vars=set([self.Bf, self.Cf]), factor_fn=phiBC)

        def phiCD(scope_product):
            ""
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

        self.CD = Factor(gid="CD", scope_vars=set([self.Cf, self.Df]), factor_fn=phiCD)

        def phiDA(scope_product):
            ""
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

        self.DA = Factor(gid="DA", scope_vars=set([self.Df, self.Af]), factor_fn=phiDA)

        # Koller, Friedman 2009 p. 107
        self.af = NumCatRVariable(
            node_id="A",
            input_data={"outcome-values": [10, 50, 20]},
            distribution=lambda x: 0.4 if x != 20 else 0.2,
        )

        def phiaB(scope_product):
            ""
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

        self.aB = Factor(gid="ab", scope_vars=set([self.af, self.Bf]), factor_fn=phiaB)

        def phibc(scope_product):
            ""
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

        self.bc = Factor(gid="bc", scope_vars=set([self.Bf, self.Cf]), factor_fn=phibc)

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
        pval = self.f.zval()
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
        self.assertTrue(mjoint, (dmarg * imarg * gmarg) / self.f.zval())

    def test_factor_product(self):
        "from Koller, Friedman 2009, p. 105, figure 4.2"
        Ab_Bc, prod1 = self.AB.product(self.BC)
        Ab_Bc_Cd, prod2 = Ab_Bc.product(self.CD)
        result, prod3 = Ab_Bc_Cd.product(self.DA)
        for sm in result.scope_products:
            sms = set(sm)
            f = result.phi(sms)
            ff = round(result.phi_normal(sms), 6)
            if sms == set([("B", 50), ("C", 50), ("A", 50), ("D", 10)]):
                self.assertEqual(f, 100000)
                self.assertEqual(ff, 0.013885)

            elif sms == set([("B", 50), ("C", 50), ("A", 50), ("D", 50)]):
                self.assertEqual(f, 100000)
                self.assertEqual(ff, 0.013885)

            elif sms == set([("B", 50), ("C", 50), ("A", 10), ("D", 10)]):
                self.assertEqual(f, 5000000)
                self.assertEqual(ff, 0.694267)

            elif sms == set([("B", 50), ("C", 50), ("A", 10), ("D", 50)]):
                self.assertEqual(f, 500)
                self.assertEqual(ff, 6.9e-05)

            elif sms == set([("B", 50), ("C", 10), ("A", 50), ("D", 10)]):
                self.assertEqual(f, 10)
                self.assertEqual(ff, 1e-06)

            elif sms == set([("B", 50), ("C", 10), ("A", 50), ("D", 50)]):
                self.assertEqual(f, 100000)
                self.assertEqual(ff, 0.013885)
            elif sms == set([("B", 50), ("C", 10), ("A", 10), ("D", 10)]):
                self.assertEqual(f, 500)
                self.assertEqual(ff, 6.9e-05)

            elif sms == set([("B", 50), ("C", 10), ("A", 10), ("D", 50)]):
                self.assertEqual(f, 500)
                self.assertEqual(ff, 6.9e-05)

            elif sms == set([("B", 10), ("C", 50), ("A", 50), ("D", 10)]):
                self.assertEqual(f, 100)
                self.assertEqual(ff, 1.4e-05)

            elif sms == set([("B", 10), ("C", 50), ("A", 50), ("D", 50)]):
                self.assertEqual(f, 100)
                self.assertEqual(ff, 1.4e-05)
            elif sms == set([("B", 10), ("C", 50), ("A", 10), ("D", 10)]):
                self.assertEqual(f, 300000)
                self.assertEqual(ff, 0.041656)

            elif sms == set([("B", 10), ("C", 50), ("A", 10), ("D", 50)]):
                self.assertEqual(f, 30)
                self.assertEqual(ff, 4e-06)

            elif sms == set([("B", 10), ("C", 10), ("A", 50), ("D", 10)]):
                self.assertEqual(f, 100)
                self.assertEqual(ff, 1.4e-05)

            elif sms == set([("B", 10), ("C", 10), ("A", 50), ("D", 50)]):
                self.assertEqual(f, 1000000)
                self.assertEqual(ff, 0.138853)

            elif sms == set([("B", 10), ("C", 10), ("A", 10), ("D", 10)]):
                self.assertEqual(f, 300000)
                self.assertEqual(ff, 0.041656)
            elif sms == set([("B", 10), ("C", 10), ("A", 10), ("D", 50)]):
                self.assertEqual(f, 300000)
                self.assertEqual(ff, 0.041656)

    def test_reduced_by_value(self):
        "from Koller, Friedman 2009, p. 111 figure 4.5"
        red = set([("C", 10)])
        aB_c, prod = self.aB.product(self.bc)
        # print(aB_c.scope_products)
        aB_c.reduced_by_value(context=red)
        # print(aB_c.scope_products)
        for p in aB_c.scope_products:
            ps = set(p)
            f = round(aB_c.phi(ps), 5)
            if ps == set([("A", 10), ("B", 50), ("C", 10)]):
                self.assertEqual(f, 0.08)
            elif ps == set([("A", 10), ("B", 10), ("C", 10)]):
                self.assertEqual(f, 0.25)
            elif ps == set([("B", 50), ("A", 20), ("C", 10)]):
                self.assertEqual(f, 0.09)
            elif ps == set([("B", 10), ("A", 20), ("C", 10)]):
                self.assertEqual(f, 0.15)
            elif ps == set([("A", 50), ("B", 50), ("C", 10)]):
                self.assertEqual(f, 0.0)
            elif ps == set([("A", 50), ("B", 10), ("C", 10)]):
                self.assertEqual(f, 0.05)

    def test_reduce_by_vars(self):
        ""
        # TODO This needs a better test
        assignments = set([("grade", 0.4)])
        var = set([self.fdice, self.grade])
        self.f.reduce_by_vars(assignment_context=var, assignments=assignments)
        com = sum([self.f.factor_fn(f) for f in [{("grade", 0.4)}]])
        self.assertEqual(self.f.Z, com)

    def test_sumout_var(self):
        "from Koller, Friedman 2009, p. 297 figure 9.7"
        aB_c, prod = self.aB.product(self.bc)
        a_c = aB_c.sumout_var(self.Bf)
        dset = self.Bf.value_set()
        for p in a_c.scope_products:
            ps = set(p)
            f = round(a_c.phi(ps), 4)
            diff = ps.difference(dset)
            if diff == set([("C", 10), ("A", 10)]):
                self.assertEqual(f, 0.33)
            elif diff == set([("C", 50), ("A", 10)]):
                self.assertEqual(f, 0.51)
            elif diff == set([("C", 10), ("A", 50)]):
                self.assertEqual(f, 0.05)
            elif diff == set([("C", 50), ("A", 50)]):
                self.assertEqual(f, 0.07)
            elif diff == set([("C", 10), ("A", 20)]):
                self.assertEqual(f, 0.24)
            elif diff == set([("C", 50), ("A", 20)]):
                self.assertEqual(f, 0.39)

    def test_maxout_var(self):
        "from Koller, Friedman 2009, p. 555 figure 13.1"
        aB_c, prod = self.aB.product(self.bc)
        a_c = aB_c.maxout_var(self.Bf)
        dset = self.Bf.value_set()
        for p in a_c.scope_products:
            ps = set(p)
            f = round(a_c.phi(ps), 4)
            diff = ps.difference(dset)
            if diff == set([("C", 10), ("A", 10)]):
                self.assertEqual(f, 0.25)
            elif diff == set([("C", 50), ("A", 10)]):
                self.assertEqual(f, 0.35)
            elif diff == set([("C", 10), ("A", 50)]):
                self.assertEqual(f, 0.05)
            elif diff == set([("C", 50), ("A", 50)]):
                self.assertEqual(f, 0.07)
            elif diff == set([("C", 10), ("A", 20)]):
                self.assertEqual(f, 0.15)
            elif diff == set([("C", 50), ("A", 20)]):
                self.assertEqual(f, 0.21)
