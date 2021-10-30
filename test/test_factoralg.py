"""!
Factor algebra test cases
"""
import math
import unittest
from random import choice

from pygmodels.factor.factor import BaseFactor, Factor
from pygmodels.factor.factorf.factoralg import FactorAlgebra
from pygmodels.factor.factorf.factorops import FactorOps
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.pgmtype.randomvariable import NumCatRVariable


class TestFactorAlg(unittest.TestCase):
    """!"""

    def data_1(self):
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
        self.AB_b = BaseFactor(
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
        self.BC_b = BaseFactor(
            gid="BC", scope_vars=set([self.Bf, self.Cf]), factor_fn=phiBC
        )

    def data_2(self):
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
        self.CD_b = BaseFactor(
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
        self.DA_b = BaseFactor(
            gid="DA", scope_vars=set([self.Df, self.Af]), factor_fn=phiDA
        )

    def setUp(self):
        """"""
        self.data_1()
        self.data_2()

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
        self.aB_b = BaseFactor(
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
        self.bc_b = BaseFactor(
            gid="bc", scope_vars=set([self.Bf, self.Cf]), factor_fn=phibc
        )

    def test_factor_product(self):
        "from Koller, Friedman 2009, p. 105, figure 4.2"
        Ab_Bc, prod1 = FactorAlgebra.product(f=self.AB, other=self.BC)
        Ab_Bc_Cd, prod2 = FactorAlgebra.product(f=Ab_Bc, other=self.CD)
        result, prod3 = FactorAlgebra.product(f=Ab_Bc_Cd, other=self.DA)
        for sm in FactorOps.cartesian(result):
            sms = set(sm)
            f = result.phi(sms)
            ff = round(FactorOps.phi_normal(result, sms), 6)
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
        aB_c, prod = FactorAlgebra.product(f=self.aB, other=self.bc)
        # print(aB_c.scope_products)
        nf = FactorAlgebra.reduced_by_value(aB_c, assignments=red)
        sps = set([frozenset(s) for s in FactorOps.cartesian(nf)])

        self.assertEqual(
            sps,
            set(
                [
                    frozenset([("A", 10), ("B", 50), ("C", 10)]),
                    frozenset([("A", 10), ("B", 10), ("C", 10)]),
                    frozenset([("B", 50), ("A", 20), ("C", 10)]),
                    frozenset([("B", 10), ("A", 20), ("C", 10)]),
                    frozenset([("A", 50), ("B", 50), ("C", 10)]),
                    frozenset([("A", 50), ("B", 10), ("C", 10)]),
                ]
            ),
        )
        for p in FactorOps.cartesian(nf):
            ps = set(p)
            f = round(nf.phi(ps), 5)
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
        """"""
        evidence = set([("C", 10), ("D", 50)])
        aB_c, prod = FactorAlgebra.product(f=self.aB, other=self.bc)
        # print(aB_c.scope_products)
        nf = FactorAlgebra.reduced_by_vars(aB_c, assignments=evidence)
        sps = set([frozenset(s) for s in FactorOps.cartesian(nf)])

        self.assertEqual(
            sps,
            set(
                [
                    frozenset([("A", 10), ("B", 50), ("C", 10)]),
                    frozenset([("A", 10), ("B", 10), ("C", 10)]),
                    frozenset([("B", 50), ("A", 20), ("C", 10)]),
                    frozenset([("B", 10), ("A", 20), ("C", 10)]),
                    frozenset([("A", 50), ("B", 50), ("C", 10)]),
                    frozenset([("A", 50), ("B", 10), ("C", 10)]),
                ]
            ),
        )

    def test_sumout_var(self):
        "from Koller, Friedman 2009, p. 297 figure 9.7"
        aB_c, prod = FactorAlgebra.product(f=self.aB, other=self.bc)
        a_c = FactorAlgebra.sumout_var(aB_c, self.Bf)
        dset = self.Bf.value_set()
        for p in FactorOps.cartesian(a_c):
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
        aB_c, prod = FactorAlgebra.product(f=self.aB, other=self.bc)
        a_c = FactorAlgebra.maxout_var(aB_c, self.Bf)
        dset = self.Bf.value_set()
        for p in FactorOps.cartesian(a_c):
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
