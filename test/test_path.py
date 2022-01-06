"""!
Test path object
"""
import unittest

from pygmodels.graph.graphmodel.graph import Graph
from pygmodels.graph.graphmodel.path import Path
from pygmodels.graph.graphops.graphops import BaseGraphOps
from pygmodels.graph.graphtype.edge import Edge, EdgeType
from pygmodels.graph.graphtype.node import Node


class PathTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # From Diestel 2017, p. 7, fig. 1.3.1
        self.n1 = Node("a", {})  # b
        self.n2 = Node("b", {})  # c
        self.n3 = Node("f", {})  # d
        self.n4 = Node("e", {})  # e
        self.n5 = Node("g", {})  # e
        self.n6 = Node("h", {})  # e
        self.n7 = Node("j", {})  # e

        self.e1 = Edge(
            "e1",
            start_node=self.n1,
            end_node=self.n2,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.e2 = Edge(
            "e2",
            start_node=self.n2,
            end_node=self.n3,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.e3 = Edge(
            "e3",
            start_node=self.n3,
            end_node=self.n4,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.e4 = Edge(
            "e4",
            start_node=self.n4,
            end_node=self.n5,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.e5 = Edge(
            "e5",
            start_node=self.n5,
            end_node=self.n6,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.e6 = Edge(
            "e6",
            start_node=self.n6,
            end_node=self.n7,
            edge_type=EdgeType.UNDIRECTED,
        )
        # n1 - n2 - n3 - n4 - n5 - n6 - n7
        #
        #
        #

        self.path = Path(
            gid="mpath",
            data={},
            edges=[self.e1, self.e2, self.e3, self.e4, self.e5, self.e6],
        )
        # tree
        self.a = Node("a")
        self.b = Node("b")
        self.c = Node("c")
        self.d = Node("d")
        self.e = Node("e")
        self.f = Node("f")
        self.g = Node("g")
        self.h = Node("h")
        self.j = Node("j")
        self.k = Node("k")
        self.m = Node("m")
        #
        #    +--a --+
        #    |      |
        #    b      c
        #    |       \
        # +--+--+     g
        # |  |  |     |
        # d  e  f     h -- j
        #       |
        #    +--+---+
        #    |      |
        #    k      m
        #
        #
        self.ab = Edge(edge_id="ab", start_node=self.a, end_node=self.b)
        self.ac = Edge(edge_id="ac", start_node=self.a, end_node=self.c)
        self.bd = Edge(edge_id="bd", start_node=self.b, end_node=self.d)
        self.be = Edge(edge_id="be", start_node=self.b, end_node=self.e)
        self.bf = Edge(edge_id="bf", start_node=self.b, end_node=self.f)
        self.fk = Edge(edge_id="fk", start_node=self.f, end_node=self.k)
        self.fm = Edge(edge_id="fm", start_node=self.f, end_node=self.m)
        self.cg = Edge(edge_id="cg", start_node=self.c, end_node=self.g)
        self.gh = Edge(edge_id="gh", start_node=self.g, end_node=self.h)
        self.hj = Edge(edge_id="hj", start_node=self.h, end_node=self.j)
        self.gtree = Graph.from_edgeset(
            edges=set(
                [
                    self.ab,
                    self.ac,
                    self.bd,
                    self.be,
                    self.bf,
                    self.fk,
                    self.fm,
                    self.cg,
                    self.gh,
                    self.hj,
                ]
            ),
        )

    def test_id(self):
        return self.assertEqual(self.path.id(), "mpath")

    def test_length(self):
        """"""
        plen = self.path.length()
        self.assertEqual(6, plen)

    def test_node_list(self):
        """"""
        nlist = self.path.node_list()
        self.assertEqual(
            nlist,
            [self.n1, self.n2, self.n3, self.n4, self.n5, self.n6, self.n7],
        )

    def test_node_list_f(self):
        """"""
        nlist = self.path.node_list()
        self.assertFalse(
            nlist
            == [self.n2, self.n1, self.n3, self.n4, self.n5, self.n6, self.n7]
        )

    def test_endvertices(self):
        """"""
        nlist = self.path.endvertices()
        self.assertEqual(nlist, (self.n1, self.n7))

    def test_from_ucs(self):
        """"""
        start_node = self.b
        goal_node = self.m
        problem_set = self.gtree.E
        p = Path.from_ucs(
            g=self.gtree,
            goal=goal_node,
            start=start_node,
            problem_set=problem_set,
        )
        self.assertEqual(p.node_list(), [self.b, self.f, self.m])


if __name__ == "__main__":
    unittest.main()
