"""
Node unit tests
"""
import unittest
from gmodels.gtype.node import Node


class NodeTest(unittest.TestCase):
    def setUp(self):
        ""
        self.node = Node(node_id="mnode", data={"my": "data"})

    def test_id(self):
        ""
        self.assertEqual(self.node.id(), "mnode")

    def test_data(self):
        ""
        self.assertEqual(self.node.data(), {"my": "data"})

    def test_equal(self):
        self.assertEqual(self.node, Node("mnode", {"my": "data"}))

    def test_str(self):
        n1 = Node("mnode", {"my": "data", "is": "awesome"})
        mstr = "mnode--my-data::is-awesome"
        self.assertEqual(str(n1), mstr)

    def test_hash(self):
        mstr = "mnode--my-data::is-awesome"
        n1 = Node("mnode", {"my": "data", "is": "awesome"})
        self.assertEqual(hash(n1), hash(mstr))


if __name__ == "__main__":
    unittest.main()
