"""!
Test undirected graph object
"""
from gmodels.undigraph import UndiGraph
from gmodels.node import Node
from gmodels.edge import Edge, EdgeType
import unittest


class UndiGraphTest(unittest.TestCase):
    ""

    def setUp(self):
        self.n1 = Node("a", {})
        self.n2 = Node("b", {})
        self.n3 = Node("f", {})
        self.n4 = Node("e", {})
        self.e1 = Edge(
            "e1", start_node=self.n1, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )
        self.e2 = Edge(
            "e2", start_node=self.n1, end_node=self.n2, edge_type=EdgeType.UNDIRECTED
        )
        self.e3 = Edge(
            "e3", start_node=self.n1, end_node=self.n3, edge_type=EdgeType.UNDIRECTED
        )
        self.e4 = Edge(
            "e4", start_node=self.n2, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )
        self.e5 = Edge(
            "e5", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )

        self.graph = UndiGraph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2, self.e3, self.e4, self.e5]),
        )

    def test_id(self):
        return self.assertEqual(self.graph.id(), "g1")

    def test_find_shortest_path(self):
        ""
        path = self.graph.find_shortest_path(n1=self.n1, n2=self.n4)
        print(path)


if __name__ == "__main__":
    unittest.main()
