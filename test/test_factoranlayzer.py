"""!
Factor analyzer test cases
"""
import math
import unittest
from random import choice

from pygmodels.factor.factor import BaseFactor, Factor
from pygmodels.factor.factorf.factoranalyzer import (
    FactorAnalyzer,
    FactorNumericAnalyzer,
)
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.pgmtype.randomvariable import NumCatRVariable


class TestFactorAnalyzer(unittest.TestCase):
    """!"""

    def setUp(self):
        """"""
        # Koller, Friedman 2009, p. 104
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

        self.bc = Factor(gid="bc", scope_vars=set([self.Bf, self.Cf]), factor_fn=phibc)
        self.bc_b = BaseFactor(
            gid="bc", scope_vars=set([self.Bf, self.Cf]), factor_fn=phibc
        )

    def test_max_value(self):
        """"""
        mval = FactorAnalyzer.max_value(self.bc)
        self.assertEqual(mval, set([("B", 10), ("C", 50)]))

    def test_max_probability(self):
        """"""
        mval = FactorNumericAnalyzer.max_probability(self.bc)
        self.assertEqual(mval, 0.7)

    def test_min_value(self):
        """"""
        mval = FactorAnalyzer.min_value(self.bc)
        self.assertEqual(mval, set([("B", 50), ("C", 10)]))

    def test_min_probability(self):
        """"""
        mval = FactorNumericAnalyzer.min_probability(self.bc)
        self.assertEqual(mval, 0.1)

    @unittest.skip("FactorAnalyzer.normalize not yet implemented")
    def test_normalize(self):
        """"""
        pass


if __name__ == "__main__":
    unittest.main()
