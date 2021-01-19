"""!
tree.py tests
"""
from gmodels.gtypes.tree import Tree
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.gtypes.node import Node
import unittest
import pprint


class TreeTest(unittest.TestCase):
    ""

    def setUp(self):
        ""
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
        self.gtree = Tree(
            gid="t",
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
        self.assertEqual(self.gtree.id(), "t")

    def test_root(self):
        self.assertEqual(self.gtree.root_node(), self.a)

    def test_leaves(self):
        ""
        self.assertEqual(
            self.gtree.leaves(), set([self.k, self.d, self.e, self.m, self.j])
        )

    def test_from_edgeset(self):
        ""
        eset = set(
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
        )
        temp = Tree.from_edgeset(eset)
        self.assertEqual(self.gtree.root_node(), temp.root_node())
        self.assertEqual(self.gtree.leaves(), temp.leaves())

    def test_upset_of(self):
        ""
        print(self.gtree.paths)


if __name__ == "__main__":
    unittest.main()
