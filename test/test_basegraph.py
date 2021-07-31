"""!
Test general BaseGraph object
"""
from pygmodels.gtype.basegraph import BaseGraph
from pygmodels.gtype.node import Node
from pygmodels.gtype.edge import Edge, EdgeType
import unittest
import pprint


class BaseGraphTest(unittest.TestCase):
    def setUp(self):
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
        self.e1 = Edge.undirected("e1", start_node=self.n1, end_node=self.n2)
        self.e2 = Edge.undirected("e2", start_node=self.n2, end_node=self.n3)
        self.e3 = Edge.undirected("e3", start_node=self.n3, end_node=self.n4)
        self.e4 = Edge.undirected("e4", start_node=self.n1, end_node=self.n4)

        self.graph = BaseGraph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2]),
        )

    def test_id(self):
        return self.assertEqual(self.graph.id(), "g1")

    def test_V(self):
        ""
        V = self.graph.V
        nodes = {"n1": self.n1, "n2": self.n2, "n3": self.n3, "n4": self.n4}
        for nid, node in nodes.copy().items():
            self.assertEqual(nid in V, nid in nodes)
            self.assertEqual(V[nid], nodes[nid])

    def test_E(self):
        ""
        E = self.graph.E

        edges = {"e1": self.e1, "e2": self.e2}
        for eid, edge in edges.copy().items():
            self.assertEqual(eid in E, eid in edges)
            self.assertEqual(E[eid], edges[eid])
