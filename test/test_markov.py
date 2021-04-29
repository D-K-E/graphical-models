"""!
Test markov network
"""

from gmodels.randomvariable import NumCatRVariable
from gmodels.markov import MarkovNetwork, ConditionalRandomField
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.gtypes.undigraph import UndiGraph
from gmodels.factor import Factor
from uuid import uuid4
import pdb

import unittest


class MarkovTest(unittest.TestCase):
    ""

    def setUp(self):
        ""
        idata = {
            "A": {"outcome-values": [True, False]},
            "B": {"outcome-values": [True, False]},
            "C": {"outcome-values": [True, False]},
            "D": {"outcome-values": [True, False]},
        }

        # misconception example
        self.A = NumCatRVariable(
            node_id="A", input_data=idata["A"], distribution=lambda x: 0.5
        )
        self.B = NumCatRVariable(
            node_id="B", input_data=idata["B"], distribution=lambda x: 0.5
        )
        self.C = NumCatRVariable(
            node_id="C", input_data=idata["C"], distribution=lambda x: 0.5
        )
        self.D = NumCatRVariable(
            node_id="D", input_data=idata["D"], distribution=lambda x: 0.5
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
            ""
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
            ""
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
            ""
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
            ""
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
            distribution=lambda x: 0.01 if x else 0.99,
        )
        self.b = NumCatRVariable(
            node_id="b", input_data=idata["B"], distribution=lambda x: 0.5
        )
        self.d = NumCatRVariable(
            node_id="d",
            input_data=idata["A"],
            distribution=lambda x: 0.7468 if x else 0.2532,
        )
        self.c = NumCatRVariable(
            node_id="c",
            input_data=idata["A"],
            distribution=lambda x: 0.7312 if x else 0.2688,
        )
        self.ab = Edge(
            "ab", start_node=self.a, end_node=self.b, edge_type=EdgeType.UNDIRECTED
        )
        self.ad = Edge(
            "ad", start_node=self.a, end_node=self.d, edge_type=EdgeType.UNDIRECTED
        )

        self.bc = Edge(
            "bc", start_node=self.b, end_node=self.c, edge_type=EdgeType.UNDIRECTED
        )
        self.dc = Edge(
            "dc", start_node=self.d, end_node=self.c, edge_type=EdgeType.UNDIRECTED
        )
        self.ugraph = UndiGraph(
            "ug1",
            data={"m": "f"},
            nodes=set([self.a, self.b, self.c, self.d]),
            edges=set([self.ab, self.ad, self.bc, self.dc]),
        )

    def test_id(self):
        ""
        self.assertEqual(self.mnetwork.id(), "mnet")

    def test_from_undigraph(self):
        ""
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
            fmax_prob = f.max_probability()
            fmax = f.max_value()
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
            #
