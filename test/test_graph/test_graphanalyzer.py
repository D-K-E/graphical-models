"""!
\file test_graphanalyzer.py Graph Analyzer Test for BaseGraph subclasses
"""
import math
import pprint
import unittest
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.graph.ganalysis.graphanalyzer import (
    BaseGraphAnalyzer,
    BaseGraphBoolAnalyzer,
    BaseGraphNodeAnalyzer,
    BaseGraphNumericAnalyzer,
)
from pygmodels.graph.graphmodel.graph import Graph
from pygmodels.graph.graphops.graphops import (
    BaseGraphBoolOps,
    BaseGraphNodeOps,
    BaseGraphOps,
)
from pygmodels.graph.graphtype.abstractobj import (
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
)
from pygmodels.graph.graphtype.basegraph import BaseGraph
from pygmodels.graph.graphtype.edge import Edge, EdgeType
from pygmodels.graph.graphtype.node import Node


class BaseGraphAnalyzerTest(unittest.TestCase):
    """"""

    def setUp(self):
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
        self.e1 = Edge(
            "e1",
            start_node=self.n1,
            end_node=self.n2,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.e2 = Edge(
            "e2",
            start_node=self.n2,
            end_node=self.n3,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.e3 = Edge(
            "e3",
            start_node=self.n3,
            end_node=self.n4,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.e4 = Edge(
            "e4",
            start_node=self.n1,
            end_node=self.n4,
            edge_type=EdgeType.UNDIRECTED,
        )

        self.graph = BaseGraph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2]),
        )
        self.graph_2 = BaseGraph(
            "g2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2, self.e3]),
        )
        #
        self.a = Node("a", {})  # b
        self.b = Node("b", {})  # c
        self.f = Node("f", {})  # d
        self.e = Node("e", {})  # e
        self.ae = Edge(
            "ae",
            start_node=self.a,
            end_node=self.e,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.ab = Edge(
            "ab",
            start_node=self.a,
            end_node=self.b,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.af = Edge(
            "af",
            start_node=self.a,
            end_node=self.f,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.be = Edge(
            "be",
            start_node=self.b,
            end_node=self.e,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.ef = Edge(
            "ef",
            start_node=self.e,
            end_node=self.f,
            edge_type=EdgeType.UNDIRECTED,
        )

        # undirected graph
        self.a = Node("a", {})  # b
        self.b = Node("b", {})  # c
        self.f = Node("f", {})  # d
        self.e = Node("e", {})  # e
        self.ae = Edge(
            "ae",
            start_node=self.a,
            end_node=self.e,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.ab = Edge(
            "ab",
            start_node=self.a,
            end_node=self.b,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.af = Edge(
            "af",
            start_node=self.a,
            end_node=self.f,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.be = Edge(
            "be",
            start_node=self.b,
            end_node=self.e,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.ef = Edge(
            "ef",
            start_node=self.e,
            end_node=self.f,
            edge_type=EdgeType.UNDIRECTED,
        )

        # undirected graph
        self.ugraph1 = Graph(
            "ug1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set(
                [
                    self.ae,
                    # self.ab,
                    self.af,
                    # self.be,
                    self.ef,
                ]
            ),
        )
        self.ugraph2 = BaseGraph(
            "ug2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set(
                [
                    self.ae,
                    self.ab,
                    self.af,
                    self.be,
                    self.ef,
                ]
            ),
        )
        # ugraph2 :
        #   +-----+
        #  /       \
        # a -- b -- e
        #  \       /
        #   +-----f

        self.ugraph3 = BaseGraph(
            "ug3",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set(
                [
                    self.ab,
                    # self.af,
                    self.be,
                ]
            ),
        )
        # ugraph3 :
        #
        #
        # a -- b -- e
        #  \
        #   +-----f

        self.ugraph4 = BaseGraph(
            "ug4",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set(self.ugraph2.V).union(self.graph_2.V),
            edges=set(self.ugraph2.E).union(self.graph_2.E),
        )
        # ugraph 4
        #   +-----+     n1 -- n2 -- n3 -- n4
        #  /       \     \                /
        # a -- b -- e     +--------------+
        #  \       /
        #   +-----f
        self.ugraph5 = Graph(
            "ug5",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set(
                [
                    self.a,
                    self.b,
                    self.e,
                    self.f,
                    self.n1,
                    self.n2,
                    self.n3,
                    self.n4,
                ]
            ),
            edges=set(
                [
                    self.ab,
                    self.af,
                    self.ae,
                    self.be,
                    self.ef,
                    self.e1,
                    self.e2,
                    self.e3,
                    self.e4,
                ]
            ),
        )

        # make some directed edges
        self.bb = Node("bb", {})
        self.cc = Node("cc", {})
        self.dd = Node("dd", {})
        self.ee = Node("ee", {})

        self.bb_cc = Edge(
            "bb_cc",
            start_node=self.bb,
            end_node=self.cc,
            edge_type=EdgeType.DIRECTED,
        )
        self.cc_dd = Edge(
            "cc_dd",
            start_node=self.cc,
            end_node=self.dd,
            edge_type=EdgeType.DIRECTED,
        )
        self.dd_ee = Edge(
            "dd_ee",
            start_node=self.dd,
            end_node=self.ee,
            edge_type=EdgeType.DIRECTED,
        )
        self.ee_bb = Edge(
            "ee_bb",
            start_node=self.ee,
            end_node=self.bb,
            edge_type=EdgeType.DIRECTED,
        )
        self.bb_dd = Edge(
            "bb_dd",
            start_node=self.bb,
            end_node=self.dd,
            edge_type=EdgeType.DIRECTED,
        )

    def test_adjmat_int(self):
        """"""
        mat = BaseGraphAnalyzer.to_adjmat(self.ugraph1)
        self.assertEqual(
            mat,
            {
                ("b", "b"): 0,
                ("b", "e"): 0,
                ("b", "f"): 0,
                ("b", "a"): 0,
                ("e", "b"): 0,
                ("e", "e"): 0,
                ("e", "f"): 1,
                ("e", "a"): 1,
                ("f", "b"): 0,
                ("f", "e"): 1,
                ("f", "f"): 0,
                ("f", "a"): 1,
                ("a", "b"): 0,
                ("a", "e"): 1,
                ("a", "f"): 1,
                ("a", "a"): 0,
            },
        )

    def test_adjmat_bool(self):
        """"""
        mat = BaseGraphAnalyzer.to_adjmat(self.ugraph1, vtype=bool)
        self.assertEqual(
            mat,
            {
                ("b", "b"): False,
                ("b", "e"): False,
                ("b", "f"): False,
                ("b", "a"): False,
                ("e", "b"): False,
                ("e", "e"): False,
                ("e", "f"): True,
                ("e", "a"): True,
                ("f", "b"): False,
                ("f", "e"): True,
                ("f", "f"): False,
                ("f", "a"): True,
                ("a", "b"): False,
                ("a", "e"): True,
                ("a", "f"): True,
                ("a", "a"): False,
            },
        )

    def test_transitive_closure_mat(self):
        """ """
        mat = BaseGraphAnalyzer.transitive_closure_matrix(self.ugraph1)
        self.assertEqual(
            mat,
            {
                ("a", "b"): True,
                ("a", "e"): True,
                ("a", "f"): True,
                ("b", "a"): False,
                ("b", "e"): False,
                ("b", "f"): False,
                ("e", "a"): True,
                ("e", "b"): True,
                ("e", "f"): True,
                ("f", "a"): True,
                ("f", "b"): True,
                ("f", "e"): True,
            },
        )

    def test_has_self_loop(self):
        """"""
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        e1 = Edge(
            "e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED
        )
        e2 = Edge(
            "e2", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED
        )
        g1 = BaseGraph("graph", nodes=set([n1, n2]), edges=set([e1, e2]))
        g2 = BaseGraph("graph", nodes=set([n1, n2]), edges=set([e1]))
        self.assertTrue(BaseGraphBoolAnalyzer.has_self_loop(g1))
        self.assertFalse(BaseGraphBoolAnalyzer.has_self_loop(g2))

    def test_is_node_independant_of(self):
        self.assertTrue(
            BaseGraphBoolAnalyzer.is_node_independent_of(
                self.graph_2, self.n1, self.n3
            )
        )

    def test_is_stable(self):
        """"""
        self.assertTrue(
            BaseGraphBoolAnalyzer.is_stable(
                self.ugraph4, set([self.a, self.n3, self.n1])
            )
        )

    def test_nb_edges(self):
        """"""
        b = BaseGraphNumericAnalyzer.nb_edges(self.graph)
        self.assertEqual(b, 2)

    def test_max_degree(self):
        """"""
        md = BaseGraphNumericAnalyzer.max_degree(self.graph)
        self.assertEqual(md, 2)

    def test_max_degree_vs(self):
        """"""
        mds = BaseGraphNodeAnalyzer.max_degree_vs(self.graph)
        self.assertEqual(mds, set([self.n2]))

    def test_min_degree(self):
        """"""
        md = BaseGraphNumericAnalyzer.min_degree(self.graph)
        self.assertEqual(md, 0)

    def test_min_degree_vs(self):
        """"""
        mds = BaseGraphNodeAnalyzer.min_degree_vs(self.graph)
        self.assertEqual(mds, set([self.n4]))

    def test_average_degree(self):
        """"""
        adeg = BaseGraphNumericAnalyzer.average_degree(self.graph)
        self.assertEqual(adeg, 1)

    def test_edge_vertex_ratio(self):
        deg = BaseGraphNumericAnalyzer.edge_vertex_ratio(self.graph)
        self.assertEqual(0.5, deg)

    def test_ev_ratio_from_average_degree(self):
        deg = BaseGraphNumericAnalyzer.ev_ratio_from_average_degree(
            self.graph, 5
        )
        self.assertEqual(2.5, deg)

    def test_ev_ratio(self):
        deg = BaseGraphNumericAnalyzer.ev_ratio(self.graph)
        self.assertEqual(0.5, deg)

    def test_order(self):
        """"""
        b = BaseGraphNumericAnalyzer.order(self.graph)
        self.assertEqual(b, 4)

    def test_is_trivial_1(self):
        """"""
        b = BaseGraphBoolAnalyzer.is_trivial(self.graph)
        self.assertFalse(b)

    def test_is_trivial_2(self):
        """"""
        n = Node("n646", {})
        e = Edge("e8", start_node=n, end_node=n, edge_type=EdgeType.UNDIRECTED)
        check = BaseGraphBoolAnalyzer.is_trivial(
            BaseGraph(gid="temp", data={}, nodes=set([n]), edges=set([e]))
        )

        self.assertTrue(check)

    def test_nb_components_wo_result(self):
        "test visit graph dfs function"
        com = BaseGraphNumericAnalyzer.nb_components(self.ugraph1)
        com2 = BaseGraphNumericAnalyzer.nb_components(self.ugraph2)
        self.assertEqual(com, 2)
        self.assertEqual(com2, 1)

    def test_nb_components_w_result(self):
        "test visit graph dfs function"
        r1 = BaseGraphAnalyzer.dfs_props(self.ugraph1)
        r2 = BaseGraphAnalyzer.dfs_props(self.ugraph2)
        com = BaseGraphNumericAnalyzer.nb_components(self.ugraph1, result=r1)
        com2 = BaseGraphNumericAnalyzer.nb_components(self.ugraph2, result=r2)
        self.assertEqual(com, 2)
        self.assertEqual(com2, 1)

    def test_is_connected_false_wo_result_f(self):
        """"""
        self.assertEqual(BaseGraphBoolAnalyzer.is_connected(self.graph), False)

    def test_is_connected_true_wo_result_t(self):
        """"""
        self.assertTrue(BaseGraphBoolAnalyzer.is_connected(self.graph_2))

    def test_is_connected_false_w_result(self):
        """"""
        result = BaseGraphAnalyzer.dfs_props(self.graph)
        self.assertEqual(
            BaseGraphBoolAnalyzer.is_connected(self.graph, result=result),
            False,
        )

    def test_is_connected_true_wo_result(self):
        """"""
        result = BaseGraphAnalyzer.dfs_props(self.graph_2)
        self.assertTrue(
            BaseGraphBoolAnalyzer.is_connected(self.graph_2, result=result)
        )

    def test_nb_neighbours_of(self):
        ndes = BaseGraphNumericAnalyzer.nb_neighbours_of(self.graph_2, self.n2)
        self.assertEqual(ndes, 2)

    @unittest.skip("test not implemented")
    def test_get_component_nodes(self):
        pass

    @unittest.skip("test not implemented")
    def test_get_components_as_node_sets(self):
        pass

    @unittest.skip("test not implemented")
    def test_get_component(self):
        pass

    def test_get_components_wo_result(self):
        """"""
        comps = BaseGraphAnalyzer.get_components(self.ugraph5)
        cs = list(comps)
        cs0ns = set(cs[0].V)
        cs0es = set(cs[0].E)
        #
        cs1ns = set(cs[1].V)
        cs1es = set(cs[1].E)
        #
        # compare graphs
        # first component
        u2nodes = set([self.a, self.b, self.e, self.f])
        u2edges = set([self.ab, self.af, self.ae, self.be, self.ef])

        # second component
        g2node = set([self.n1, self.n2, self.n3, self.n4])
        g2edge = set([self.e1, self.e2, self.e3, self.e4])
        #
        cond1 = u2nodes == cs0ns or u2nodes == cs1ns
        #
        cond2 = g2node == cs0ns or g2node == cs1ns
        #
        cond3 = u2edges == cs0es or u2edges == cs1es
        cond4 = g2edge == cs0es or g2edge == cs1es
        self.assertTrue(cond1)
        self.assertTrue(cond2)
        self.assertTrue(cond3)
        self.assertTrue(cond4)

    def test_get_components_w_result(self):
        """"""
        r1 = BaseGraphAnalyzer.dfs_props(self.ugraph5)
        comps = BaseGraphAnalyzer.get_components(self.ugraph5, result=r1)
        cs = list(comps)
        cs0ns = set(cs[0].V)
        cs0es = set(cs[0].E)
        #
        cs1ns = set(cs[1].V)
        cs1es = set(cs[1].E)
        #
        # compare graphs
        # first component
        u2nodes = set([self.a, self.b, self.e, self.f])
        u2edges = set([self.ab, self.af, self.ae, self.be, self.ef])

        # second component
        g2node = set([self.n1, self.n2, self.n3, self.n4])
        g2edge = set([self.e1, self.e2, self.e3, self.e4])
        #
        cond1 = u2nodes == cs0ns or u2nodes == cs1ns
        #
        cond2 = g2node == cs0ns or g2node == cs1ns
        #
        cond3 = u2edges == cs0es or u2edges == cs1es
        cond4 = g2edge == cs0es or g2edge == cs1es
        self.assertTrue(cond1)
        self.assertTrue(cond2)
        self.assertTrue(cond3)
        self.assertTrue(cond4)


if __name__ == "__main__":
    unittest.main()
