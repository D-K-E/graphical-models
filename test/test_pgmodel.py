"""!
Test probabilistic graph model
"""

import cProfile
import pdb
import unittest

# profiler related
from pstats import Stats
from uuid import uuid4

from pygmodels.factor.factor import Factor
from pygmodels.factor.factorf.factoralg import FactorAlgebra
from pygmodels.factor.factorf.factorops import FactorOps
from pygmodels.graph.gtype.edge import Edge, EdgeType
from pygmodels.pgm.pgmtype.pgmodel import PGModel, min_unmarked_neighbours
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable


class PGModelTest(unittest.TestCase):
    """
    PGModel tests
    """

    def cls_nodes_1(cls):
        """"""
        idata = {
            "a": {"outcome-values": [True, False]},
            "b": {"outcome-values": [True, False]},
            "c": {"outcome-values": [True, False]},
        }
        cls.a = NumCatRVariable(
            node_id="a",
            input_data=idata["a"],
            marginal_distribution=lambda x: 0.6 if x else 0.4,
        )
        cls.b = NumCatRVariable(
            node_id="b",
            input_data=idata["b"],
            marginal_distribution=lambda x: 0.5 if x else 0.5,
        )
        cls.c = NumCatRVariable(
            node_id="c",
            input_data=idata["c"],
            marginal_distribution=lambda x: 0.5 if x else 0.5,
        )
        cls.ab = Edge(
            edge_id="ab",
            edge_type=EdgeType.UNDIRECTED,
            start_node=cls.a,
            end_node=cls.b,
        )
        cls.bc = Edge(
            edge_id="bc",
            edge_type=EdgeType.UNDIRECTED,
            start_node=cls.b,
            end_node=cls.c,
        )

        def phi_ba(scope_product):
            """"""
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
            """"""
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

        cls.ba_f = Factor(
            gid="ba", scope_vars=set([cls.b, cls.a]), factor_fn=phi_ba
        )
        cls.cb_f = Factor(
            gid="cb", scope_vars=set([cls.c, cls.b]), factor_fn=phi_cb
        )
        cls.a_f = Factor(gid="a", scope_vars=set([cls.a]), factor_fn=phi_a)

    def cls_nodes_2(cls):
        """"""
        odata = {"outcome-values": [True, False]}
        cls.J = NumCatRVariable(
            node_id="J", input_data=odata, marginal_distribution=lambda x: 0.5
        )
        cls.Irvar = NumCatRVariable(
            node_id="I", input_data=odata, marginal_distribution=lambda x: 0.5
        )
        cls.X = NumCatRVariable(
            node_id="X", input_data=odata, marginal_distribution=lambda x: 0.5
        )
        cls.Y = NumCatRVariable(
            node_id="Y", input_data=odata, marginal_distribution=lambda x: 0.5
        )
        cls.Orvar = NumCatRVariable(
            node_id="O", input_data=odata, marginal_distribution=lambda x: 0.5
        )
        cls.JX = Edge(
            edge_id="JX",
            edge_type=EdgeType.DIRECTED,
            start_node=cls.J,
            end_node=cls.X,
        )
        cls.JY = Edge(
            edge_id="JY",
            edge_type=EdgeType.DIRECTED,
            start_node=cls.J,
            end_node=cls.Y,
        )
        cls.IX = Edge(
            edge_id="IX",
            edge_type=EdgeType.DIRECTED,
            start_node=cls.Irvar,
            end_node=cls.X,
        )
        cls.XO = Edge(
            edge_id="XO",
            edge_type=EdgeType.DIRECTED,
            start_node=cls.X,
            end_node=cls.Orvar,
        )
        cls.YO = Edge(
            edge_id="YO",
            edge_type=EdgeType.DIRECTED,
            start_node=cls.Y,
            end_node=cls.Orvar,
        )

        def phi_ij(scope_product, i: str):
            """"""
            ss = set(scope_product)
            if ss == set([(i, True)]):
                return 0.5
            elif ss == set([(i, False)]):
                return 0.5
            else:
                raise ValueError("unknown scope product")

        def phi_i(scope_product):
            """"""
            return phi_ij(scope_product, i="I")

        cls.I_f = Factor(
            gid="I_f", scope_vars=set([cls.Irvar]), factor_fn=phi_i
        )

        def phi_j(scope_product):
            """"""
            return phi_ij(scope_product, i="J")

        cls.J_f = Factor(gid="J_f", scope_vars=set([cls.J]), factor_fn=phi_j)

        def phi_jy(scope_product):
            """"""
            ss = set(scope_product)
            if ss == set([("J", True), ("Y", True)]):
                return 0.01
            elif ss == set([("J", True), ("Y", False)]):
                return 0.99
            elif ss == set([("J", False), ("Y", True)]):
                return 0.99
            elif ss == set([("J", False), ("Y", False)]):
                return 0.01
            else:
                raise ValueError("scope product unknown")

        cls.JY_f = Factor(
            gid="JY_f", scope_vars=set([cls.J, cls.Y]), factor_fn=phi_jy
        )

    def cls_nodes_3(cls):
        """"""
        cls.cls_nodes_2()

        def phi_ijx(scope_product):
            """"""
            ss = set(scope_product)
            if ss == set([("I", True), ("J", True), ("X", True)]):
                return 0.95
            elif ss == set([("I", True), ("J", True), ("X", False)]):
                return 0.05
            elif ss == set([("I", True), ("J", False), ("X", True)]):
                return 0.05
            elif ss == set([("I", True), ("J", False), ("X", False)]):
                return 0.95
            elif ss == set([("I", False), ("J", True), ("X", True)]):
                return 0.05
            elif ss == set([("I", False), ("J", True), ("X", False)]):
                return 0.95
            elif ss == set([("I", False), ("J", False), ("X", True)]):
                return 0.05
            elif ss == set([("I", False), ("J", False), ("X", False)]):
                return 0.95
            else:
                raise ValueError("scope product unknown")

        cls.IJX_f = Factor(
            gid="IJX_f",
            scope_vars=set([cls.J, cls.X, cls.Irvar]),
            factor_fn=phi_ijx,
        )

        def phi_xyo(scope_product):
            """"""
            ss = set(scope_product)
            if ss == set([("X", True), ("Y", True), ("O", True)]):
                return 0.98
            elif ss == set([("X", True), ("Y", True), ("O", False)]):
                return 0.02
            elif ss == set([("X", True), ("Y", False), ("O", True)]):
                return 0.98
            elif ss == set([("X", True), ("Y", False), ("O", False)]):
                return 0.02
            elif ss == set([("X", False), ("Y", True), ("O", True)]):
                return 0.98
            elif ss == set([("X", False), ("Y", True), ("O", False)]):
                return 0.02
            elif ss == set([("X", False), ("Y", False), ("O", True)]):
                return 0.02
            elif ss == set([("X", False), ("Y", False), ("O", False)]):
                return 0.98
            else:
                raise ValueError("scope product unknown")

        cls.XYO_f = Factor(
            gid="XYO_f",
            scope_vars=set([cls.Y, cls.X, cls.Orvar]),
            factor_fn=phi_xyo,
        )

    def setUp(self):
        """!
        Graph made from values of
        Darwiche 2009, p. 132, figure 6.4
        """
        self.cls_nodes_1()
        self.cls_nodes_2()
        self.cls_nodes_3()
        self.pgm = PGModel(
            gid="pgm",
            nodes=set([self.a, self.b, self.c]),
            edges=set([self.ab, self.bc]),
            factors=set([self.ba_f, self.cb_f, self.a_f]),
        )

        # most probable explanation instantiations
        # graph

        self.pgm_mpe = PGModel(
            gid="mpe",
            nodes=set([self.J, self.Y, self.X, self.Irvar, self.Orvar]),
            edges=set([self.JY, self.JX, self.YO, self.IX, self.XO]),
            factors=set(
                [self.I_f, self.J_f, self.JY_f, self.IJX_f, self.XYO_f]
            ),
        )

        # profiler code
        # initialize profiler
        self.verbose = False
        self.prof = cProfile.Profile()
        self.prof.enable()
        # print("\n<<<<--------")

    def tearDown(self):
        """ """
        p = Stats(self.prof)
        p.sort_stats("cumtime")
        if self.verbose:
            p.dump_stats("profiles/test_graph.py.prof")
        p.strip_dirs()
        # p.print_stats()
        # print("\n--------->>>")

    def test_id(self):
        """"""
        self.assertEqual(self.pgm.id(), "pgm")

    def test_markov_blanket(self):
        """"""
        self.assertEqual(self.pgm.markov_blanket(self.a), set([self.b]))

    def test_factors(self):
        """"""
        self.assertEqual(
            self.pgm.factors(), set([self.ba_f, self.cb_f, self.a_f])
        )

    def test_closure_of(self):
        """"""
        self.assertEqual(self.pgm.closure_of(self.a), set([self.b, self.a]))

    def test_conditionaly_independent_of_t(self):
        """"""
        self.assertEqual(
            self.pgm.is_conditionaly_independent_of(self.a, self.c), True
        )

    def test_conditionaly_independent_of_f(self):
        """"""
        # pdb.set_trace()
        iscond = self.pgm.is_conditionaly_independent_of(self.a, self.b)
        self.assertEqual(iscond, False)

    def test_scope_of(self):
        """"""
        self.assertEqual(self.pgm.scope_of(self.ba_f), set([self.a, self.b]))

    def test_is_scope_subset_of_t(self):
        """"""
        self.assertEqual(
            self.pgm.is_scope_subset_of(
                self.ba_f, set([self.a, self.b, self.c])
            ),
            True,
        )

    def test_is_scope_subset_of_f(self):
        """"""
        self.assertEqual(
            self.pgm.is_scope_subset_of(self.ba_f, set([self.c])), False
        )

    def test_scope_subset_factors(self):
        """"""
        self.assertEqual(
            self.pgm.scope_subset_factors(set([self.c, self.a, self.b])),
            set([self.ba_f, self.cb_f, self.a_f]),
        )

    def test_get_factor_product_var(self):
        """"""
        p, f, of = self.pgm.get_factor_product_var(
            fs=self.pgm.factors(), Z=self.a
        )
        self.assertEqual(f, set([self.a_f, self.ba_f]))
        self.assertEqual(of, set([self.cb_f]))
        afbf, v = FactorAlgebra.product(f=self.a_f, other=self.ba_f)
        for pr in FactorOps.cartesian(afbf):
            prs = set(pr)
            for psp in FactorOps.cartesian(p):
                psps = set(psp)
                if prs.issubset(psps) is True:
                    self.assertEqual(afbf.phi(prs), p.phi(psps))

    def test_sum_prod_var_eliminate(self):
        """!
        based on values of Darwiche 2009 p. 133
        """
        ofacs = self.pgm.sum_prod_var_eliminate(
            factors=self.pgm.factors(), Z=self.a
        )
        smf = [o for o in ofacs if o.id() != "cb"][0]
        for s in FactorOps.cartesian(smf):
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
        for sp in FactorOps.cartesian(p):
            sps = set(sp)
            res = round(p.phi(sps), 4)
            if set([("c", True)]).issubset(sps):
                self.assertEqual(res, 0.376)
            elif set([("c", False)]).issubset(sps):
                self.assertEqual(res, 0.624)

    def test_order_by_greedy_metric(self):
        """!"""
        ns = set([self.a, self.b])
        cards = self.pgm.order_by_greedy_metric(
            nodes=ns, s=min_unmarked_neighbours
        )
        self.assertEqual(cards, {"a": 0, "b": 1})
        ns = set([self.c, self.b])
        cards2 = self.pgm.order_by_greedy_metric(
            nodes=ns, s=min_unmarked_neighbours
        )
        self.assertEqual(cards2, {"c": 0, "b": 1})
        ns = set([self.c, self.a])
        cards3 = self.pgm.order_by_greedy_metric(
            nodes=ns, s=min_unmarked_neighbours
        )
        self.assertTrue(
            cards3 == {"a": 0, "c": 1} or cards3 == {"a": 1, "c": 0}
        )

    def test_reduce_factors_with_evidence(self):
        """"""
        ev = set([("a", True), ("b", True)])
        fs, es = self.pgm.reduce_factors_with_evidence(ev)
        fs_s = set(
            [
                frozenset([frozenset(s) for s in FactorOps.cartesian(f)])
                for f in fs
            ]
        )
        self.assertEqual(
            fs_s,
            set(
                [
                    frozenset(
                        [
                            frozenset(s)
                            for s in FactorOps.cartesian(
                                FactorAlgebra.reduced_by_value(self.ba_f, ev)
                            )
                        ]
                    ),
                    frozenset(
                        [
                            frozenset(s)
                            for s in FactorOps.cartesian(
                                FactorAlgebra.reduced_by_value(self.a_f, ev)
                            )
                        ]
                    ),
                    frozenset(
                        [
                            frozenset(s)
                            for s in FactorOps.cartesian(
                                FactorAlgebra.reduced_by_value(self.cb_f, ev)
                            )
                        ]
                    ),
                ]
            ),
        )

    def test_cond_prod_by_variable_elimination(self):
        """!
        Test based on the computation in Darwiche 2009, p. 140
        """
        ev = set([("a", True)])
        qs = set([self.c])
        p, a = self.pgm.cond_prod_by_variable_elimination(qs, ev)
        # check if it is a valid marginal_distribution
        s = 0
        for ps in FactorOps.cartesian(p):
            pss = set(ps)
            f = round(FactorOps.phi_normal(p, pss), 4)
            s += f
            if set([("c", True)]) == pss:
                self.assertEqual(f, 0.32)
            elif set([("c", False)]) == pss:
                self.assertEqual(f, 0.68)
        self.assertTrue(s, 1.0)

    def test_mpe_prob(self):
        """!
        From Darwiche 2009, p. 250
        """
        ev = set([("J", True), ("O", False)])
        prob = self.pgm_mpe.mpe_prob(evidences=ev)
        self.assertEqual(round(prob, 5), 0.23042)

    def test_max_product_ve(self):
        """!
        From Darwiche 2009, p. 250
        """
        ev = set([("J", True), ("O", False)])
        assignments, fac, f = self.pgm_mpe.max_product_ve(evidences=ev)
        assign = set([a for a in assignments.items()])
        possibles = [
            set(
                [
                    ("J", True),
                    ("O", False),
                    ("X", False),
                    ("Y", False),
                    ("I", False),
                ]
            ),
            set(
                [
                    ("J", True),
                    ("O", False),
                    ("X", False),
                    ("Y", False),
                    ("I", True),
                ]
            ),
        ]
        cond = assign == possibles[0] or assign == possibles[1]
        self.assertTrue(cond)


if __name__ == "__main__":
    unittest.main()
