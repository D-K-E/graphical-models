"""!
Factor analyzer test cases
"""
from gmodels.pgmtypes.factor import Factor, BaseFactor
from gmodels.fops.factoranalyzer import FactorAnalyzer
from gmodels.pgmtypes.randomvariable import NumCatRVariable
from gmodels.gtypes.edge import Edge, EdgeType
import unittest
from random import choice
import math


class TestFactorAnalyzer(unittest.TestCase):
    """!
    """

    def setUp(self):
        ""
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
        self.bc_b = BaseFactor(
            gid="bc", scope_vars=set([self.Bf, self.Cf]), factor_fn=phibc
        )

    def test_cls_max_value(self):
        ""
        mval = FactorAnalyzer.cls_max_value(self.bc)
        self.assertEqual(mval, set([("B", 10), ("C", 50)]))

    def test_cls_max_probability(self):
        ""
        mval = FactorAnalyzer.cls_max_probability(self.bc)
        self.assertEqual(mval, 0.7)

    def test_cls_min_value(self):
        ""
        mval = FactorAnalyzer.cls_min_value(self.bc)
        self.assertEqual(mval, set([("B", 50), ("C", 10)]))

    def test_cls_min_probability(self):
        ""
        mval = FactorAnalyzer.cls_min_probability(self.bc)
        self.assertEqual(mval, 0.1)

    def test_max_value(self):
        ""
        mval = FactorAnalyzer(self.bc_b).max_value()
        self.assertEqual(mval, set([("B", 10), ("C", 50)]))

    def test_max_probability(self):
        ""
        mval = FactorAnalyzer(self.bc_b).max_probability()
        self.assertEqual(mval, 0.7)

    def test_min_value(self):
        ""
        mval = FactorAnalyzer(self.bc_b).min_value()
        self.assertEqual(mval, set([("B", 50), ("C", 10)]))

    def test_min_probability(self):
        ""
        mval = FactorAnalyzer(self.bc_b).min_probability()
        self.assertEqual(mval, 0.1)

    @unittest.skip("FactorAnalyzer.normalize not yet implemented")
    def test_normalize(self):
        ""
        pass


if __name__ == "__main__":
    unittest.main()
