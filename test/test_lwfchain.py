"""!
test lwf chain graph test
"""
from gmodels.pgmodel import PGModel
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.factor import Factor
from gmodels.randomvariable import NumCatRVariable
from gmodels.lwfchain import LWFChainGraph
from uuid import uuid4

import unittest


class LWFChainGraphTest(unittest.TestCase):
    ""

    def setUp(self):
        ""

    def test_id(self):
        ""
        self.assertEqual(self.pgm.id(), "pgm")
