"""!
Test general Graph object
"""
from pygmodels.gmodel.finitegraph import FiniteGraph
from pygmodels.gtype.node import Node
from pygmodels.gtype.edge import Edge, EdgeType
import unittest
import pprint


class FiniteGraphTest(unittest.TestCase):
    def setUp(self):
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
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

        self.graph = FiniteGraph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2]),
        )

    def test_id(self):
        return self.assertEqual(self.graph.id(), "g1")
