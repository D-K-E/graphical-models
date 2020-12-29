"""
test info object
"""
import unittest
from gmodels.info import EdgeInfo
from gmodels.abstractobj import EdgeType


class EdgeInfoTest(unittest.TestCase):
    ""

    def setUp(self):
        ""
        self.info = EdgeInfo(edge_id="edge id", etype=EdgeType.DIRECTED)

    def test_id(self):
        ""
        self.assertEqual("edge id", self.info.id(), "id not equal")

    def test_type(self):
        ""
        self.assertEqual(EdgeType.DIRECTED, self.info.type(), "type not equal")

    def test_str(self):
        ""
        einfo = str(self.info)
        self.assertEqual("edge id--1", einfo, "string representation not equal")

    def test_hash(self):
        ""
        ehash = hash(self.info)
        shash = hash("edge id--1")
        self.assertEqual(ehash, shash, "hash are not equal")

    def test_equal(self):
        ""
        ninfo = EdgeInfo(edge_id="edge id", etype=EdgeType.DIRECTED)
        self.assertEqual(ninfo, self.info, "edge info are not equal")


if __name__ == "__main__":
    unittest.main()
