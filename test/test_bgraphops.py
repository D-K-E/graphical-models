"""!
\file test_bgraphops.py Test BaseGraphOps object
"""
from typing import Set, Optional, Callable, List, Tuple, Union, Dict, FrozenSet
from pygmodels.gtype.abstractobj import AbstractGraph, AbstractUndiGraph
from pygmodels.gtype.abstractobj import AbstractGraph, AbstractDiGraph
from pygmodels.gtype.abstractobj import AbstractNode, AbstractEdge
from pygmodels.gtype.basegraph import BaseGraph
from pygmodels.graphf.bgraphops import BaseGraphOps

from pygmodels.gtype.node import Node
from pygmodels.gtype.edge import Edge, EdgeType

from uuid import uuid4
import math
import unittest


class BaseGraphOpsTest(unittest.TestCase):
    ""

    def setUp(self):
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
        nset = set([self.n1, self.n2, self.n3, self.n4, self.n5])
        self.e1 = Edge(
            "e1", start_node=self.n1, end_node=self.n2, edge_type=EdgeType.UNDIRECTED
        )
        self.e2 = Edge(
            "e2", start_node=self.n2, end_node=self.n3, edge_type=EdgeType.UNDIRECTED
        )
        self.e3 = Edge(
            "e3", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )
        self.e4 = Edge(
            "e4", start_node=self.n1, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
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
            "ae", start_node=self.a, end_node=self.e, edge_type=EdgeType.UNDIRECTED
        )
        self.ab = Edge(
            "ab", start_node=self.a, end_node=self.b, edge_type=EdgeType.UNDIRECTED
        )
        self.af = Edge(
            "af", start_node=self.a, end_node=self.f, edge_type=EdgeType.UNDIRECTED
        )
        self.be = Edge(
            "be", start_node=self.b, end_node=self.e, edge_type=EdgeType.UNDIRECTED
        )
        self.ef = Edge(
            "ef", start_node=self.e, end_node=self.f, edge_type=EdgeType.UNDIRECTED
        )

        # undirected graph
        self.ugraph2 = BaseGraph(
            "ug2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set([self.ae, self.ab, self.af, self.be, self.ef,]),
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
            nodes=BaseGraphOps.nodes(self.ugraph2).union(
                BaseGraphOps.nodes(self.graph_2)
            ),
            edges=BaseGraphOps.edges(self.ugraph2).union(
                BaseGraphOps.edges(self.graph_2)
            ),
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
            "bb_cc", start_node=self.bb, end_node=self.cc, edge_type=EdgeType.DIRECTED
        )
        self.cc_dd = Edge(
            "cc_dd", start_node=self.cc, end_node=self.dd, edge_type=EdgeType.DIRECTED
        )
        self.dd_ee = Edge(
            "dd_ee", start_node=self.dd, end_node=self.ee, edge_type=EdgeType.DIRECTED
        )
        self.ee_bb = Edge(
            "ee_bb", start_node=self.ee, end_node=self.bb, edge_type=EdgeType.DIRECTED
        )
        self.bb_dd = Edge(
            "bb_dd", start_node=self.bb, end_node=self.dd, edge_type=EdgeType.DIRECTED
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
        ""
        edges = BaseGraphOps.edges_of(self.graph, self.n2)
        self.assertEqual(edges, set([self.e1, self.e2]))

    def test_outgoing_edges_of(self):
        ""
        edges = BaseGraphOps.outgoing_edges_of(self.graph, self.n2)
        self.assertEqual(edges, frozenset([self.e2, self.e1]))

    def test_incoming_edges_of(self):
        ""
        edges = BaseGraphOps.incoming_edges_of(self.graph, self.n2)
        self.assertEqual(edges, frozenset([self.e1, self.e2]))

    def test_is_in_true(self):
        ""
        b = BaseGraphOps.is_in(self.graph, self.n2)
        self.assertTrue(b)

    def test_is_in_false(self):
        ""
        n = Node("n86", {})
        b = BaseGraphOps.is_in(self.graph, n)
        self.assertFalse(b)

    def test_vertex_by_id(self):
        n = BaseGraphOps.vertex_by_id(self.graph, "n1")
        self.assertEqual(n, self.n1)

    def test_edge_by_id(self):
        e = BaseGraphOps.edge_by_id(self.graph, "e1")
        self.assertEqual(e, self.e1)

    def test_edge_by_vertices(self):
        e = BaseGraphOps.edge_by_vertices(self.graph, self.n2, self.n3)
        self.assertEqual(e, set([self.e2]))

    def test_edge_by_vertices_n(self):
        check = False
        try:
            e = BaseGraphOps.edge_by_vertices(self.graph, self.n1, self.n3)
        except ValueError:
            check = True
        self.assertTrue(check)

    def test_edges_by_end(self):
        ""
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        e1 = Edge("e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED)
        e2 = Edge("e2", start_node=n1, end_node=n1, edge_type=EdgeType.UNDIRECTED)
        g = BaseGraph("g", nodes=set([n1, n2]), edges=set([e1, e2]))
        self.assertEqual(BaseGraphOps.edges_by_end(g, n2), set([e1]))

    def test_vertices_of(self):
        ""
        vertices = BaseGraphOps.vertices_of(self.graph, self.e2)
        self.assertEqual(vertices, (self.n2, self.n3))


if __name__ == "__main__":
    unittest.main()
