# simple tests for different queues

from gmodels.gtypes.queue import PriorityQueue
from gmodels.gtypes.node import Node
from gmodels.gtypes.edge import Edge, EdgeType

import unittest


class PriorityQueueTest(unittest.TestCase):
    ""

    def setUp(self):
        """
        """
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.e1 = Edge(
            "e1", start_node=self.n1, end_node=self.n2, edge_type=EdgeType.DIRECTED
        )
        self.e2 = Edge(
            "e2", start_node=self.n2, end_node=self.n3, edge_type=EdgeType.DIRECTED
        )
        self.q = PriorityQueue(is_min=True)
        self.q.insert(2, self.n1)
        self.q.insert(5, self.n2)
        self.q.insert(1, self.n3)
        self.qm = PriorityQueue(is_min=False)
        self.qm.insert(2, self.n1)
        self.qm.insert(5, self.n2)
        self.qm.insert(1, self.n3)

    def test_insert_min(self):
        ""
        self.minq = PriorityQueue(is_min=True)
        self.minq.insert(2, self.n1)
        self.minq.insert(5, self.n2)
        self.minq.insert(1, self.n3)
        self.assertEqual(self.minq.queue, [(1, self.n3), (2, self.n1), (5, self.n2)])

    def test_insert_max(self):
        ""
        self.maxq = PriorityQueue(is_min=False)
        self.maxq.insert(2, self.n1)
        self.maxq.insert(5, self.n2)
        self.maxq.insert(1, self.n3)
        self.assertEqual(
            self.maxq.queue, list(reversed([(1, self.n3), (2, self.n1), (5, self.n2)]))
        )

    def test_key(self):
        ""
        k = self.q.key(self.n1)
        self.assertEqual(k, 2)

    def test_values(self):
        ""
        k = self.q.values(2)
        self.assertEqual(k, set([self.n1]))

    def test_min_min(self):
        k, v = self.q.min()
        self.assertEqual(k, 1)
        self.assertEqual(v, self.n3)

    def test_max_min(self):
        k, v = self.q.max()
        self.assertEqual(k, 5)
        self.assertEqual(v, self.n2)

    def test_min_max(self):
        k, v = self.qm.min()
        self.assertEqual(k, 1)
        self.assertEqual(v, self.n3)

    def test_max_max(self):
        k, v = self.qm.max()
        self.assertEqual(k, 5)
        self.assertEqual(v, self.n2)


if __name__ == "__main__":
    unittest.main()
