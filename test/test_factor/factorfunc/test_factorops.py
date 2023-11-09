"""!
Factor operators test cases
"""
import math
import unittest
from random import choice

from pygmodels.factor.factor import BaseFactor, Factor
from pygmodels.factor.factorfunc.factorops import FactorOps
from pygmodels.graph.graphtype.edge import Edge, EdgeType
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable


class TestFactorOps(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
