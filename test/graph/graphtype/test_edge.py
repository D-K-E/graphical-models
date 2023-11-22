"""!
Edge unit tests
"""
import unittest

from pygmodels.graph.graphtype.edge import Edge, EdgeType
from pygmodels.graph.graphtype.node import Node


class EdgeTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        n1 = Node("m1", {})
        n2 = Node("m2", {})
        self.dedge = Edge(
            edge_id="medge",
            start_node=n1,
            end_node=n2,
            edge_type=EdgeType.DIRECTED,
            data={"my": "data"},
        )
        self.uedge = Edge(
            edge_id="uedge",
            start_node=n1,
            end_node=n2,
            edge_type=EdgeType.UNDIRECTED,
            data={"my": "data"},
        )

    def test_id(self):
        """"""
        self.assertEqual(self.uedge.id, "uedge")

    def test_type(self):
        """"""
        self.assertEqual(self.uedge.type, EdgeType.UNDIRECTED)

    def test_start(self):
        self.assertEqual(self.uedge.start, Node("m1", {}))

    def test_end(self):
        self.assertEqual(self.uedge.end, Node("m2", {}))

    def test_node_ids(self):
        self.assertEqual(self.uedge.node_ids, set(["m1", "m2"]))

    def test_is_endvertice_true(self):
        """"""
        positive = self.uedge.is_endvertice(Node("m1", {}))
        self.assertEqual(positive, True)

    def test_is_endvertice_false(self):
        """"""
        negative = self.uedge.is_endvertice(Node("m3", {}))
        self.assertEqual(negative, False)


if __name__ == "__main__":
    unittest.main()
