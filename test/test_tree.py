"""!
tree.py tests
"""
import pprint
import unittest

from pygmodels.gmodel.tree import Tree
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.gtype.node import Node


class TreeTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
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
        self.assertEqual(self.gtree.root, self.a)

    def test_leaves(self):
        """"""
        self.assertEqual(
            self.gtree.leaves(), set([self.k, self.d, self.e, self.m, self.j])
        )

    def test_from_edgeset(self):
        """"""
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
        self.assertEqual(self.gtree.root, temp.root)
        self.assertEqual(self.gtree.leaves(), temp.leaves())

    def test_height_of(self):
        """"""
        c = self.gtree.height_of(self.g)
        self.assertEqual(c, 2)

    def test_is_upclosure_of_t(self):
        """"""
        c = self.gtree.is_upclosure_of(self.g, self.k)
        self.assertTrue(c)

    def test_is_upclosure_of_f(self):
        """"""
        c = self.gtree.is_upclosure_of(self.g, self.b)
        self.assertFalse(c)

    def test_is_downclosure_of_t(self):
        """"""
        c = self.gtree.is_downclosure_of(self.g, self.k)
        self.assertFalse(c)

    def test_is_downclosure_of_f(self):
        """"""
        c = self.gtree.is_downclosure_of(self.g, self.b)
        self.assertTrue(c)

    def test_upset_of_t(self):
        """"""
        uset = self.gtree.upset_of(self.k)
        self.assertTrue(uset == set([self.k, self.m, self.h, self.j]))

    def test_upset_of_f(self):
        """"""
        uset = self.gtree.upset_of(self.k)
        self.assertFalse(uset == set([self.k, self.m, self.h, self.b]))

    def test_downset_of_t(self):
        """"""
        uset = self.gtree.downset_of(self.b)
        self.assertTrue(uset == set([self.b, self.a, self.c]))

    def test_downset_of_f(self):
        """"""
        uset = self.gtree.downset_of(self.b)
        self.assertFalse(uset == set([self.b, self.a, self.d]))

    def test_extract_path(self):
        """"""
        p = self.gtree.extract_path(start=self.b, end=self.m)
        self.assertEqual(p.node_list(), [self.b, self.f, self.m])


if __name__ == "__main__":
    unittest.main()
