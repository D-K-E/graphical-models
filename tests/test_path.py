"""!
Test path object
"""
from gmodels.path import Path
from gmodels.graph import Graph
from gmodels.node import Node
from gmodels.edge import Edge, EdgeType
import unittest


class PathTest(unittest.TestCase):
    ""

    def setUp(self):
        self.n1 = Node("a", {})  # b
        self.n2 = Node("b", {})  # c
        self.n3 = Node("f", {})  # d
        self.n4 = Node("e", {})  # e
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

        # undirected graph
        self.ugraph = Graph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2, self.e3, self.e4, self.e5]),
        )

        # make some directed edges
        self.e6 = Edge(
            "e6", start_node=self.n1, end_node=self.n3, edge_type=EdgeType.DIRECTED
        )
        self.e7 = Edge(
            "e7", start_node=self.n3, end_node=self.n2, edge_type=EdgeType.DIRECTED
        )
        self.e8 = Edge(
            "e8", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.DIRECTED
        )
        self.e9 = Edge(
            "e9", start_node=self.n4, end_node=self.n2, edge_type=EdgeType.DIRECTED
        )
        self.e10 = Edge(
            "e10", start_node=self.n4, end_node=self.n1, edge_type=EdgeType.DIRECTED
        )
        self.dgraph = Graph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e6, self.e7, self.e8, self.e9, self.e10]),
        )
        self.path = Path(
            gid="mpath",
            data={},
            nodes=[self.n1, self.n2, self.n4],
            edges=[self.e2, self.e4, self.e5],
        )

    def test_id(self):
        return self.assertEqual(self.path.id(), "mpath")

    def test_length(self):
        ""
        plen = self.path.length()
        self.assertEqual(3, plen)

    def test_node_list(self):
        ""
        nlist = self.path.node_list()
        self.assertEqual(nlist, [self.n1, self.n2, self.n4])

    def test_node_list_f(self):
        ""
        nlist = self.path.node_list()
        self.assertFalse(nlist == [self.n2, self.n1, self.n4])

    def test_endvertices(self):
        ""
        nlist = self.path.endvertices()
        self.assertEqual(nlist, (self.n1, self.n4))


if __name__ == "__main__":
    unittest.main()
