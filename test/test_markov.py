"""!
Test markov network
"""

import math
import pdb
import unittest
from random import choice
from uuid import uuid4

from pygmodels.factorf.factoranalyzer import FactorAnalyzer
from pygmodels.gmodel.undigraph import UndiGraph
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.pgmodel.markov import ConditionalRandomField, MarkovNetwork
from pygmodels.pgmtype.factor import Factor
from pygmodels.pgmtype.randomvariable import NumCatRVariable


class MarkovTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        idata = {
            "A": {"outcome-values": [True, False]},
            "B": {"outcome-values": [True, False]},
            "C": {"outcome-values": [True, False]},
            "D": {"outcome-values": [True, False]},
        }

        # misconception example: Koller, Friedman, 2009 p. 104
        self.A = NumCatRVariable(
            node_id="A",
            input_data=idata["A"],
            marginal_distribution=lambda x: 0.5,
        )
        self.B = NumCatRVariable(
            node_id="B",
            input_data=idata["B"],
            marginal_distribution=lambda x: 0.5,
        )
        self.C = NumCatRVariable(
            node_id="C",
            input_data=idata["C"],
            marginal_distribution=lambda x: 0.5,
        )
        self.D = NumCatRVariable(
            node_id="D",
            input_data=idata["D"],
            marginal_distribution=lambda x: 0.5,
        )
        self.AB = Edge(
            edge_id="AB",
            edge_type=EdgeType.UNDIRECTED,
            start_node=self.A,
            end_node=self.B,
        )
        self.AD = Edge(
            edge_id="AD",
            edge_type=EdgeType.UNDIRECTED,
            start_node=self.A,
            end_node=self.D,
        )
        self.DC = Edge(
            edge_id="DC",
            edge_type=EdgeType.UNDIRECTED,
            start_node=self.D,
            end_node=self.C,
        )
        self.BC = Edge(
            edge_id="BC",
            edge_type=EdgeType.UNDIRECTED,
            start_node=self.B,
            end_node=self.C,
        )

        def phi_AB(scope_product):
            """"""
            ss = frozenset(scope_product)
            if ss == frozenset([("A", False), ("B", False)]):
                return 30.0
            elif ss == frozenset([("A", False), ("B", True)]):
                return 5.0
            elif ss == frozenset([("A", True), ("B", False)]):
                return 1.0
            elif ss == frozenset([("A", True), ("B", True)]):
                return 10.0
            else:
                raise ValueError("product error")

        def phi_BC(scope_product):
            """"""
            ss = frozenset(scope_product)
            if ss == frozenset([("B", False), ("C", False)]):
                return 100.0
            elif ss == frozenset([("B", False), ("C", True)]):
                return 1.0
            elif ss == frozenset([("B", True), ("C", False)]):
                return 1.0
            elif ss == frozenset([("B", True), ("C", True)]):
                return 100.0
            else:
                raise ValueError("product error")

        def phi_CD(scope_product):
            """"""
            ss = frozenset(scope_product)
            if ss == frozenset([("C", False), ("D", False)]):
                return 1.0
            elif ss == frozenset([("C", False), ("D", True)]):
                return 100.0
            elif ss == frozenset([("C", True), ("D", False)]):
                return 100.0
            elif ss == frozenset([("C", True), ("D", True)]):
                return 1.0
            else:
                raise ValueError("product error")

        def phi_DA(scope_product):
            """"""
            ss = frozenset(scope_product)
            if ss == frozenset([("D", False), ("A", False)]):
                return 100.0
            elif ss == frozenset([("D", False), ("A", True)]):
                return 1.0
            elif ss == frozenset([("D", True), ("A", False)]):
                return 1.0
            elif ss == frozenset([("D", True), ("A", True)]):
                return 100.0
            else:
                raise ValueError("product error")

        self.AB_f = Factor(
            gid="ab_f", scope_vars=set([self.A, self.B]), factor_fn=phi_AB
        )
        self.BC_f = Factor(
            gid="bc_f", scope_vars=set([self.B, self.C]), factor_fn=phi_BC
        )
        self.CD_f = Factor(
            gid="cd_f", scope_vars=set([self.C, self.D]), factor_fn=phi_CD
        )
        self.DA_f = Factor(
            gid="da_f", scope_vars=set([self.D, self.A]), factor_fn=phi_DA
        )

        self.mnetwork = MarkovNetwork(
            gid="mnet",
            nodes=set([self.A, self.B, self.C, self.D]),
            edges=set([self.AB, self.AD, self.BC, self.DC]),
            factors=set([self.DA_f, self.CD_f, self.BC_f, self.AB_f]),
        )
        # CH-Asia values from Cowell 2005, p. 116 table 6.9
        self.a = NumCatRVariable(
            node_id="a",
            input_data=idata["A"],
            marginal_distribution=lambda x: 0.01 if x else 0.99,
        )
        self.b = NumCatRVariable(
            node_id="b",
            input_data=idata["B"],
            marginal_distribution=lambda x: 0.5,
        )
        self.d = NumCatRVariable(
            node_id="d",
            input_data=idata["A"],
            marginal_distribution=lambda x: 0.7468 if x else 0.2532,
        )
        self.c = NumCatRVariable(
            node_id="c",
            input_data=idata["A"],
            marginal_distribution=lambda x: 0.7312 if x else 0.2688,
        )
        self.ab = Edge(
            "ab",
            start_node=self.a,
            end_node=self.b,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.ad = Edge(
            "ad",
            start_node=self.a,
            end_node=self.d,
            edge_type=EdgeType.UNDIRECTED,
        )

        self.bc = Edge(
            "bc",
            start_node=self.b,
            end_node=self.c,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.dc = Edge(
            "dc",
            start_node=self.d,
            end_node=self.c,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.ugraph = UndiGraph(
            "ug1",
            data={"m": "f"},
            nodes=set([self.a, self.b, self.c, self.d]),
            edges=set([self.ab, self.ad, self.bc, self.dc]),
        )
        #
        # Conditional Random Field test
        # from Koller, Friedman 2009, p. 144-145, example 4.20
        self.X_1 = NumCatRVariable(
            node_id="X_1",
            input_data=idata["A"],
            marginal_distribution=lambda x: 0.5,
        )
        self.X_2 = NumCatRVariable(
            node_id="X_2",
            input_data=idata["A"],
            marginal_distribution=lambda x: 0.5,
        )
        self.X_3 = NumCatRVariable(
            node_id="X_3",
            input_data=idata["A"],
            marginal_distribution=lambda x: 0.5,
        )
        self.Y_1 = NumCatRVariable(
            node_id="Y_1",
            input_data=idata["A"],
            marginal_distribution=lambda x: 0.5,
        )
        self.X1_Y1 = Edge(
            edge_id="X1_Y1",
            edge_type=EdgeType.UNDIRECTED,
            start_node=self.X_1,
            end_node=self.Y_1,
        )
        self.X2_Y1 = Edge(
            edge_id="X2_Y1",
            edge_type=EdgeType.UNDIRECTED,
            start_node=self.X_2,
            end_node=self.Y_1,
        )
        self.X3_Y1 = Edge(
            edge_id="X3_Y1",
            edge_type=EdgeType.UNDIRECTED,
            start_node=self.X_3,
            end_node=self.Y_1,
        )

        def phi_X1_Y1(scope_product):
            """"""
            w = 0.5
            ss = frozenset(scope_product)
            if ss == frozenset([("X_1", True), ("Y_1", True)]):
                return math.exp(1.0 * w)
            else:
                return math.exp(0.0)

        def phi_X2_Y1(scope_product):
            """"""
            w = 5.0
            ss = frozenset(scope_product)
            if ss == frozenset([("X_2", True), ("Y_1", True)]):
                return math.exp(1.0 * w)
            else:
                return math.exp(0.0)

        def phi_X3_Y1(scope_product):
            """"""
            w = 9.4
            ss = frozenset(scope_product)
            if ss == frozenset([("X_3", True), ("Y_1", True)]):
                return math.exp(1.0 * w)
            else:
                return math.exp(0.0)

        def phi_Y1(scope_product):
            """"""
            w = 0.6
            ss = frozenset(scope_product)
            if ss == frozenset([("Y_1", True)]):
                return math.exp(1.0 * w)
            else:
                return math.exp(0.0)

        self.X1_Y1_f = Factor(
            gid="x1_y1_f",
            scope_vars=set([self.X_1, self.Y_1]),
            factor_fn=phi_X1_Y1,
        )
        self.X2_Y1_f = Factor(
            gid="x2_y1_f",
            scope_vars=set([self.X_2, self.Y_1]),
            factor_fn=phi_X2_Y1,
        )
        self.X3_Y1_f = Factor(
            gid="x3_y1_f",
            scope_vars=set([self.X_3, self.Y_1]),
            factor_fn=phi_X3_Y1,
        )
        self.Y1_f = Factor(
            gid="y1_f", scope_vars=set([self.Y_1]), factor_fn=phi_Y1
        )

        self.crf_koller = ConditionalRandomField(
            "crf",
            observed_vars=set([self.X_1, self.X_2, self.X_3]),
            target_vars=set([self.Y_1]),
            edges=set([self.X1_Y1, self.X2_Y1, self.X3_Y1]),
            factors=set([self.X1_Y1_f, self.X2_Y1_f, self.X3_Y1_f, self.Y1_f]),
        )

    def test_id(self):
        """"""
        self.assertEqual(self.mnetwork.id(), "mnet")

    def test_cond_prod_by_variable_elimination(self):
        """
        \brief compare values from Koller, Friedman, 2009 p. 108

        """
        query_vars = set([self.A, self.B])
        prob, a = self.mnetwork.cond_prod_by_variable_elimination(
            queries=query_vars, evidences=set()
        )
        q1 = set([("A", False), ("B", False)])
        f1 = round(prob.phi_normal(q1), 3)
        self.assertEqual(f1, 0.125)

        q2 = set([("A", False), ("B", True)])
        f2 = round(prob.phi_normal(q2), 2)
        self.assertEqual(f2, 0.69)

        q3 = set([("A", True), ("B", False)])
        f3 = round(prob.phi_normal(q3), 2)
        self.assertEqual(f3, 0.14)

        q4 = set([("A", True), ("B", True)])
        f4 = round(prob.phi_normal(q4), 2)
        self.assertEqual(f4, 0.04)

    def test_from_undigraph(self):
        """"""
        markov = MarkovNetwork.from_undigraph(udi=self.ugraph)
        factors = markov.factors()
        # a - d
        a_d_max = 0.99 * 0.7468
        # b - c
        b_c_max = 0.5 * 0.7312
        # a - b
        a_b_max = 0.99 * 0.5
        # c - d
        c_d_max = 0.7468 * 0.7312
        for f in factors:
            fmax_prob = FactorAnalyzer.cls_max_probability(f)
            fmax = FactorAnalyzer.cls_max_value(f)
            svars = set([s.id() for s in f.scope_vars()])
            if svars == set(["a", "d"]):
                mval = set([("a", False), ("d", True)])
                self.assertEqual(mval, fmax)
                self.assertEqual(a_d_max, fmax_prob)
            elif svars == set(["b", "c"]):
                mval = set([("b", True), ("c", True)])
                mval2 = set([("b", False), ("c", True)])
                self.assertTrue(mval == fmax or mval2 == fmax)
                self.assertEqual(b_c_max, fmax_prob)
            elif svars == set(["a", "b"]):
                mval = set([("a", False), ("b", True)])
                mval2 = set([("a", False), ("b", False)])
                self.assertTrue(mval == fmax or mval2 == fmax)
                self.assertEqual(a_b_max, fmax_prob)
            else:
                mval = set([("c", True), ("d", True)])
                self.assertEqual(mval, fmax)
                self.assertEqual(c_d_max, fmax_prob)

            self.assertEqual(round(f.zval(), 3), 1.0)

    def test_crf_target_zero(self):
        """!
        Koller, Friedman 2009, p. 145, example 4.20
        """
        ev = set([("Y_1", False)])
        qs = set([self.X_1, self.X_2, self.X_3])
        qqs = set(
            [
                ("X_1", choice([False, True])),
                ("X_2", choice([False, True])),
                ("X_3", choice([False, True])),
            ]
        )
        foo1, a1 = self.crf_koller.cond_prod_by_variable_elimination(
            queries=qs, evidences=ev
        )
        foo2, a2 = self.crf_koller.cond_prod_by_variable_elimination(
            queries=qs, evidences=ev
        )

        self.assertEqual(foo1.phi(qqs), 1.0)
        self.assertTrue(foo2.phi(qqs) != 1.0)
