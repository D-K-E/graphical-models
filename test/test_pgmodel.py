"""!
Test probabilistic graph model
"""

from gmodels.pgmodel import PGModel
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.factor import Factor
from gmodels.randomvariable import NumCatRVariable
from uuid import uuid4

import unittest


class PGModelTest(unittest.TestCase):
    ""

    def setUp(self):
        """!
        Graph made from values of
        Darwiche 2009, p. 132, figure 6.4
        """
        idata = {
            "a": {"outcome-values": [True, False]},
            "b": {"outcome-values": [True, False]},
            "c": {"outcome-values": [True, False]},
        }
        self.a = NumCatRVariable(
            node_id="a", input_data=idata["a"], distribution=lambda x: 0.6 if x else 0.4
        )
        self.b = NumCatRVariable(
            node_id="b", input_data=idata["b"], distribution=lambda x: 0.5 if x else 0.5
        )
        self.c = NumCatRVariable(
            node_id="c", input_data=idata["c"], distribution=lambda x: 0.5 if x else 0.5
        )
        self.ab = Edge(
            edge_id="ab",
            edge_type=EdgeType.UNDIRECTED,
            start_node=self.a,
            end_node=self.b,
        )
        self.bc = Edge(
            edge_id="bc",
            edge_type=EdgeType.UNDIRECTED,
            start_node=self.b,
            end_node=self.c,
        )

        def phi_ba(scope_product):
            ""
            ss = set(scope_product)
            if ss == set([("a", True), ("b", True)]):
                return 0.9
            elif ss == set([("a", True), ("b", False)]):
                return 0.1
            elif ss == set([("a", False), ("b", True)]):
                return 0.2
            elif ss == set([("a", False), ("b", False)]):
                return 0.8
            else:
                raise ValueError("product error")

        def phi_cb(scope_product):
            ""
            ss = set(scope_product)
            if ss == set([("c", True), ("b", True)]):
                return 0.3
            elif ss == set([("c", True), ("b", False)]):
                return 0.5
            elif ss == set([("c", False), ("b", True)]):
                return 0.7
            elif ss == set([("c", False), ("b", False)]):
                return 0.5
            else:
                raise ValueError("product error")

        def phi_a(scope_product):
            s = set(scope_product)
            if s == set([("a", True)]):
                return 0.6
            elif s == set([("a", False)]):
                return 0.4
            else:
                raise ValueError("product error")

        self.ba_f = Factor(gid="ba", scope_vars=set([self.b, self.a]), factor_fn=phi_ba)
        self.cb_f = Factor(gid="cb", scope_vars=set([self.c, self.b]), factor_fn=phi_cb)
        self.a_f = Factor(gid="a", scope_vars=set([self.a]), factor_fn=phi_a)

        self.pgm = PGModel(
            gid="pgm",
            nodes=set([self.a, self.b, self.c]),
            edges=set([self.ab, self.bc]),
            factors=set([self.ba_f, self.cb_f, self.a_f]),
        )

    def test_id(self):
        ""
        self.assertEqual(self.pgm.id(), "pgm")

    def test_markov_blanket(self):
        ""
        self.assertEqual(self.pgm.markov_blanket(self.a), set([self.b]))

    def test_factors(self):
        ""
        self.assertEqual(self.pgm.factors(), set([self.ba_f, self.cb_f, self.a_f]))

    def test_closure_of(self):
        ""
        self.assertEqual(self.pgm.closure_of(self.a), set([self.b, self.a]))

    def test_conditionaly_independent_of_t(self):
        ""
        self.assertEqual(self.pgm.is_conditionaly_independent_of(self.a, self.c), True)

    def test_conditionaly_independent_of_f(self):
        ""
        self.assertEqual(self.pgm.is_conditionaly_independent_of(self.a, self.b), False)

    def test_scope_of(self):
        ""
        self.assertEqual(self.pgm.scope_of(self.ba_f), set([self.a, self.b]))

    def test_is_scope_subset_of_t(self):
        ""
        self.assertEqual(
            self.pgm.is_scope_subset_of(self.ba_f, set([self.a, self.b, self.c])), True
        )

    def test_is_scope_subset_of_f(self):
        ""
        self.assertEqual(self.pgm.is_scope_subset_of(self.ba_f, set([self.c])), False)

    def test_scope_subset_factors(self):
        ""
        self.assertEqual(
            self.pgm.scope_subset_factors(set([self.c, self.a, self.b])),
            set([self.ba_f, self.cb_f, self.a_f]),
        )

    def test_get_factor_product_var(self):
        ""
        p, f, of = self.pgm.get_factor_product_var(fs=self.pgm.factors(), Z=self.a)
        self.assertEqual(f, set([self.a_f, self.ba_f]))
        self.assertEqual(of, set([self.cb_f]))
        afbf, v = self.a_f.product(self.ba_f)
        for pr in afbf.scope_products:
            prs = set(pr)
            for psp in p.scope_products:
                psps = set(psp)
                if prs.issubset(psps) is True:
                    self.assertEqual(afbf.phi(prs), p.phi(psps))

    def test_sum_prod_var_eliminate(self):
        """!
        based on values of Darwiche 2009 p. 133
        """
        ofacs = self.pgm.sum_prod_var_eliminate(factors=self.pgm.factors(), Z=self.a)
        smf = [o for o in ofacs if o.id() != "cb"][0]
        for s in smf.scope_products:
            ss = set(s)
            f = round(smf.phi(ss), 3)
            if set([("b", True)]).issubset(ss):
                self.assertEqual(f, 0.62)
            elif set([("b", False)]).issubset(ss):
                self.assertEqual(f, 0.38)

    def test_sum_product_elimination(self):
        """!
        based on values of Darwiche 2009 p. 133
        """
        p = self.pgm.sum_product_elimination(
            factors=self.pgm.factors(), Zs=[self.a, self.b]
        )
        for sp in p.scope_products:
            sps = set(sp)
            res = round(p.phi(sps), 4)
            if set([("c", True)]).issubset(sps):
                self.assertEqual(res, 0.376)
            elif set([("c", False)]).issubset(sps):
                self.assertEqual(res, 0.624)

    def test_order_by_greedy_metric(self):
        ""
        ns = set([self.a, self.b])
        cards = self.pgm.order_by_greedy_metric(
            nodes=ns, s=self.pgm.min_unmarked_neighbours
        )
        self.assertEqual(cards, {"a": 0, "b": 1})
        ns = set([self.c, self.b])
        cards2 = self.pgm.order_by_greedy_metric(
            nodes=ns, s=self.pgm.min_unmarked_neighbours
        )
        self.assertEqual(cards2, {"c": 0, "b": 1})
        ns = set([self.c, self.a])
        cards3 = self.pgm.order_by_greedy_metric(
            nodes=ns, s=self.pgm.min_unmarked_neighbours
        )
        self.assertTrue(cards3 == {"a": 0, "c": 1} or cards3 == {"a": 1, "c": 0})


if __name__ == "__main__":
    unittest.main()
