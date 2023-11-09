"""!
\file test_bgraphops.py Test BaseGraphOps object
"""
import math
import unittest
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.graph.graphops.graphops import (
    BaseGraphBoolOps,
    BaseGraphEdgeOps,
    BaseGraphNodeOps,
    BaseGraphOps,
)
from pygmodels.graph.graphtype.abstractobj import (
    AbstractDiGraph,
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
    AbstractUndiGraph,
)
from pygmodels.graph.graphtype.basegraph import BaseGraph
from pygmodels.graph.graphtype.edge import Edge, EdgeType
from pygmodels.graph.graphtype.node import Node


class BaseGraphOpsTest(unittest.TestCase):
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
        #
        self.ugraph1 = BaseGraph(
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

        # undirected graph
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

    def test_to_edgelist(self):
        gdata = BaseGraphOps.to_edgelist(self.graph)
        mdata = gdata
        gdata = {"n4": [], "n1": ["e1"], "n3": ["e2"], "n2": ["e1", "e2"]}
        for k, vs in mdata.copy().items():
            self.assertEqual(k in mdata, k in gdata)
            for v in vs:
                self.assertEqual(v in mdata[k], v in gdata[k])

    #
    def test_edges_of(self):
        """"""
        edges = BaseGraphEdgeOps.edges_of(self.graph, self.n2)
        self.assertEqual(edges, set([self.e1, self.e2]))

    def test_outgoing_edges_of(self):
        """"""
        edges = BaseGraphEdgeOps.outgoing_edges_of(self.graph, self.n2)
        self.assertEqual(edges, frozenset([self.e2, self.e1]))

    def test_incoming_edges_of(self):
        """"""
        edges = BaseGraphEdgeOps.incoming_edges_of(self.graph, self.n2)
        self.assertEqual(edges, frozenset([self.e1, self.e2]))

    def test_is_in_true(self):
        """"""
        b = BaseGraphBoolOps.is_in(self.graph, self.n2)
        self.assertTrue(b)

    def test_is_in_false(self):
        """"""
        n = Node("n86", {})
        b = BaseGraphBoolOps.is_in(self.graph, n)
        self.assertFalse(b)

    def test_vertex_by_id(self):
        n = BaseGraphNodeOps.vertex_by_id(self.graph, "n1")
        self.assertEqual(n, self.n1)

    def test_edge_by_id(self):
        e = BaseGraphEdgeOps.edge_by_id(self.graph, "e1")
        self.assertEqual(e, self.e1)

    def test_edge_by_vertices(self):
        e = BaseGraphEdgeOps.edge_by_vertices(self.graph, self.n2, self.n3)
        self.assertEqual(e, set([self.e2]))

    def test_edge_by_vertices_n(self):
        check = False
        try:
            BaseGraphEdgeOps.edge_by_vertices(self.graph, self.n1, self.n3)
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_edges_by_end(self):
        """"""
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        e1 = Edge(
            "e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED
        )
        e2 = Edge(
            "e2", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED
        )
        g = BaseGraph("g", nodes=set([n1, n2]), edges=set([e1, e2]))
        self.assertEqual(BaseGraphEdgeOps.edges_by_end(g, n2), set([e1]))

    def test_vertices_of(self):
        """"""
        vertices = BaseGraphNodeOps.vertices_of(self.graph, self.e2)
        self.assertEqual(vertices, (self.n2, self.n3))

    def test_adjmat_int(self):
        """"""
        mat = BaseGraphOps.to_adjmat(self.ugraph1)
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
        mat = BaseGraphOps.to_adjmat(self.ugraph1, vtype=bool)
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

    def test_is_adjacent_of(self):
        self.assertTrue(
            BaseGraphBoolOps.is_adjacent_of(self.graph_2, self.e2, self.e3)
        )

    def test_is_node_incident(self):
        """"""
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        e1 = Edge(
            "e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED
        )
        e2 = Edge(
            "e2", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED
        )
        self.assertTrue(
            BaseGraphBoolOps.is_node_incident(self.graph, self.n1, self.e1)
        )
        self.assertFalse(BaseGraphBoolOps.is_node_incident(self.graph, n2, e2))

    @unittest.skip("Test not yet implemented")
    def test_get_subgraph_by_vertices(self):
        raise NotImplementedError

    def test_is_neighbour_of_true(self):
        isneighbor = BaseGraphBoolOps.is_neighbour_of(
            self.graph_2, self.n2, self.n3
        )
        self.assertTrue(isneighbor)

    def test_is_neighbour_of_false(self):
        isneighbor = BaseGraphBoolOps.is_neighbour_of(
            self.graph_2, self.n2, self.n2
        )
        self.assertFalse(isneighbor)

    def test_neighbours_of(self):
        ndes = set(
            [
                n.id()
                for n in BaseGraphNodeOps.neighbours_of(self.graph_2, self.n2)
            ]
        )
        self.assertEqual(ndes, set([self.n1.id(), self.n3.id()]))


if __name__ == "__main__":
    unittest.main()
