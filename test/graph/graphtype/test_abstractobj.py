"""
"""
import unittest

from pygmodels.graph.graphtype.abstractobj import EdgeType


class EdgeTypeTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        self.edir = EdgeType.DIRECTED
        self.eudir = EdgeType.UNDIRECTED

    def test_is_directed(self):
        """"""
        self.assertEqual(self.edir.value, 1)

    def test_is_undirected(self):
        """"""
        self.assertEqual(self.eudir.value, 2)


if __name__ == "__main__":
    unittest.main()
