"""!
Test directed graph object
"""
import pdb
import pprint
import unittest

from pygmodels.graph.graphmodel.digraph import DiGraph
from pygmodels.graph.graphfunc.graphops import (
    BaseGraphEdgeOps,
    BaseGraphNodeOps,
    BaseGraphOps,
)
from pygmodels.graph.graphtype.edge import Edge, EdgeType
from pygmodels.graph.graphtype.node import Node


class DiGraphTest(unittest.TestCase):
    """!"""

    def setUp(self):
        #
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
        self.e1 = Edge.directed("e1", start_node=self.n1, end_node=self.n2)
        self.e2 = Edge.directed("e2", start_node=self.n2, end_node=self.n3)
        self.e3 = Edge.directed("e3", start_node=self.n3, end_node=self.n4)
        self.e4 = Edge.directed("e4", start_node=self.n1, end_node=self.n4)
        self.graph_2 = DiGraph(
            "g2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2, self.e3, self.e4]),
        )
        #
        # n1 → n2 → n3 → n4
        # |              ↑
        # +--------------+

        self.a = Node("a", {})  # b
        self.b = Node("b", {})  # c
        self.c = Node("c", {})
        self.d = Node("d", {})
        self.f = Node("f", {})  # d
        self.e = Node("e", {})  # e
        self.g = Node("g", {})
        self.h = Node("h", {})
        self.ae = Edge.directed("ae", start_node=self.a, end_node=self.e)
        self.ab = Edge.directed("ab", start_node=self.a, end_node=self.b)
        self.af = Edge.directed("af", start_node=self.a, end_node=self.f)
        self.ah = Edge.directed("ah", start_node=self.a, end_node=self.h)
        self.bh = Edge.directed("bh", start_node=self.b, end_node=self.h)
        self.be = Edge.directed("be", start_node=self.b, end_node=self.e)
        self.ef = Edge.directed("ef", start_node=self.e, end_node=self.f)
        self.de = Edge.directed("de", start_node=self.d, end_node=self.e)
        self.df = Edge.directed("df", start_node=self.d, end_node=self.f)
        self.cd = Edge.directed("cd", start_node=self.c, end_node=self.d)
        self.cg = Edge.directed("cg", start_node=self.c, end_node=self.g)
        self.gd = Edge.directed("gd", start_node=self.g, end_node=self.d)
        self.bg = Edge.directed("bg", start_node=self.b, end_node=self.g)
        self.fg = Edge.directed("fg", start_node=self.f, end_node=self.g)
        self.bc = Edge.directed("bc", start_node=self.b, end_node=self.c)

        # directed graph
        self.dgraph1 = DiGraph(
            "dg1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set(
                [
                    self.ae,
                    # self.ab,
                    self.af,
                    # self.be,
                    self.ef,
                ]
            ),
        )
        # dgraph1:
        #
        #
        # a --------> e  b
        # |           |
        # +---> f <---+
        #

        self.dgraph2 = DiGraph(
            "dg2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set(
                [
                    self.ae,
                    self.ab,
                    self.af,
                    self.be,
                    self.ef,
                ]
            ),
        )
        # dgraph2 :
        #
        # a -> b -> e -> f
        # |         ↑    ↑
        # +---------+----+

        self.dgraph3 = DiGraph(
            "dg3",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.e, self.f]),
            edges=set(
                [
                    self.ab,
                    self.af,
                    self.be,
                ]
            ),
        )
        # dgraph3 :
        #
        # a -> b -> e
        #  \
        #   +---> f

        self.dgraph4 = DiGraph(
            "dg4",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set(self.dgraph2.V).union(set(self.graph_2.V)),
            edges=set(self.dgraph2.E).union(set(self.graph_2.E)),
        )
        # dgraph 4
        #
        # a -> b -> e -> f   n1 -> n2 -> n3 -> n4
        # |         ↑    ↑   |                  ↑
        # +---------+----+   +------------------+

        self.e_n = Edge.directed("en", start_node=self.e, end_node=self.n1)

        self.dgraph5 = DiGraph(
            "dg5",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.c, self.d, self.e, self.f, self.g]),
            edges=set(
                [
                    self.ab,
                    self.bc,
                    self.bg,
                    self.cd,
                    self.gd,
                    self.df,
                    self.de,
                    self.ef,
                ]
            ),
        )
        # dgraph 5
        #        +--> c        +---> e
        #       /      \      /      |
        # a -> b        +--> d       |
        #       \      /      \      v
        #        +--> g        +---> f

        self.dgraph6 = DiGraph(
            "dg6",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set(
                [
                    self.a,
                    self.b,
                    self.c,
                    self.d,
                    self.e,
                    self.f,
                    self.g,
                    self.h,
                ]
            ),
            edges=set(
                [
                    self.ab,
                    self.ah,
                    self.bc,
                    self.bh,
                    self.cd,
                    self.de,
                    self.df,
                    self.cg,
                    self.fg,
                ]
            ),
        )
        # dgraph 6
        #  a       e<----d--+
        #  | \           ↑  |
        #  |  +--> b-->c-+  ↓
        #  |  |          |  f
        #  ↓  |          |  |
        #  h<-+          +--+->g

    def test_id(self):
        return self.assertEqual(self.dgraph1.id, "dg1")

    def test_find_shortest_path(self):
        """"""
        path_props = self.dgraph4.find_shortest_paths(n=self.n1)
        self.assertEqual(path_props.path_set, set([self.n1, self.n2, self.n3, self.n4]))

    def test_check_for_path_false(self):
        v = self.dgraph4.check_for_path(self.n1, self.a)
        self.assertFalse(v)

    def test_check_for_path_true(self):
        v = self.dgraph4.check_for_path(self.n1, self.n2)
        self.assertTrue(v)

    def test_outgoing_edges_of_1(self):
        """"""
        out_edges1 = BaseGraphEdgeOps.outgoing_edges_of(self.graph_2, self.n1)
        comp1 = frozenset([self.e1, self.e4])
        self.assertEqual(out_edges1, comp1)

    def test_outgoing_edges_of_2(self):
        """"""
        out_edges2 = BaseGraphEdgeOps.outgoing_edges_of(self.graph_2, self.n2)
        comp2 = frozenset([self.e2])
        self.assertEqual(out_edges2, comp2)

    def test_incoming_edges_of_1(self):
        """"""
        out_edges1 = BaseGraphEdgeOps.incoming_edges_of(self.graph_2, self.n1)
        comp1 = frozenset()
        self.assertEqual(out_edges1, comp1)

    def test_incoming_edges_of_2(self):
        """"""
        out_edges2 = BaseGraphEdgeOps.incoming_edges_of(self.graph_2, self.n2)
        comp2 = frozenset([self.e1])
        self.assertEqual(out_edges2, comp2)

    @unittest.skip("Reference found but not implemented yet")
    def test_find_transitive_closure(self):
        "Nuutila 1995 p. 14 - 15"
        #
        # Input graph
        #
        #      +--> v2 ---+           +---> v5 <----> v7
        #      |    |     |           |     ^
        # v1---+    |     +--> v4 ----+     |
        # ^         |     |           |     |
        # |         v     |           +---> v6 <----> v8
        # ----------v3----+
        #
        v1 = Node("v1", {})
        v2 = Node("v2", {})
        v3 = Node("v3", {})
        v4 = Node("v4", {})
        v5 = Node("v5", {})
        v6 = Node("v6", {})
        v7 = Node("v7", {})
        v8 = Node("v8", {})

        ev1v2 = Edge.directed("ev1v2", start_node=v1, end_node=v2)

        ev2v3 = Edge.directed("ev2v3", start_node=v2, end_node=v3)
        ev2v4 = Edge.directed("ev2v4", start_node=v2, end_node=v4)

        ev3v1 = Edge.directed("ev3v1", start_node=v3, end_node=v1)
        ev3v4 = Edge.directed("ev3v4", start_node=v3, end_node=v4)

        ev4v5 = Edge.directed("ev4v5", start_node=v4, end_node=v5)
        ev4v6 = Edge.directed("ev4v6", start_node=v4, end_node=v6)

        ev5v7 = Edge.directed("ev5v7", start_node=v5, end_node=v7)

        ev6v5 = Edge.directed("ev6v5", start_node=v6, end_node=v5)
        ev6v8 = Edge.directed("ev6v8", start_node=v6, end_node=v8)

        ev7v5 = Edge.directed("ev7v5", start_node=v7, end_node=v5)

        ev8v6 = Edge.directed("ev8v6", start_node=v8, end_node=v6)

        ing = DiGraph(
            "g2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([v1, v2, v3, v4, v5, v6, v7, v8]),
            edges=set(
                [
                    ev1v2,
                    ev2v3,
                    ev2v4,
                    ev3v1,
                    ev3v4,
                    ev4v5,
                    ev4v6,
                    ev5v7,
                    ev6v5,
                    ev6v8,
                    ev7v5,
                    ev8v6,
                ]
            ),
        )

        # Output graph
        oev1v1 = Edge.directed("oev1v1", start_node=v1, end_node=v1)
        oev1v2 = Edge.directed("oev1v2", start_node=v1, end_node=v2)
        oev1v3 = Edge.directed("oev1v3", start_node=v1, end_node=v3)
        oev1v4 = Edge.directed("oev1v4", start_node=v1, end_node=v4)
        oev1v5 = Edge.directed("oev1v5", start_node=v1, end_node=v5)
        oev1v6 = Edge.directed("oev1v6", start_node=v1, end_node=v6)
        oev1v7 = Edge.directed("oev1v7", start_node=v1, end_node=v7)
        oev1v8 = Edge.directed("oev1v8", start_node=v1, end_node=v8)
        #
        oev2v1 = Edge.directed("oev2v1", start_node=v2, end_node=v1)
        oev2v2 = Edge.directed("oev2v2", start_node=v2, end_node=v2)
        oev2v3 = Edge.directed("oev2v3", start_node=v2, end_node=v3)
        oev2v4 = Edge.directed("oev2v4", start_node=v2, end_node=v4)
        oev2v5 = Edge.directed("oev2v5", start_node=v2, end_node=v5)
        oev2v6 = Edge.directed("oev2v6", start_node=v2, end_node=v6)
        oev2v7 = Edge.directed("oev2v7", start_node=v2, end_node=v7)
        oev2v8 = Edge.directed("oev2v8", start_node=v2, end_node=v8)
        #
        oev3v1 = Edge.directed("oev3v1", start_node=v3, end_node=v1)
        oev3v2 = Edge.directed("oev3v2", start_node=v3, end_node=v2)
        oev3v3 = Edge.directed("oev3v3", start_node=v3, end_node=v3)
        oev3v4 = Edge.directed("oev3v4", start_node=v3, end_node=v4)
        oev3v5 = Edge.directed("oev3v5", start_node=v3, end_node=v5)
        oev3v6 = Edge.directed("oev3v6", start_node=v3, end_node=v6)
        oev3v7 = Edge.directed("oev3v7", start_node=v3, end_node=v7)
        oev3v8 = Edge.directed("oev3v8", start_node=v3, end_node=v8)
        #
        oev4v5 = Edge.directed("oev4v5", start_node=v4, end_node=v5)
        oev4v6 = Edge.directed("oev4v6", start_node=v4, end_node=v6)
        oev4v7 = Edge.directed("oev4v7", start_node=v4, end_node=v7)
        oev4v8 = Edge.directed("oev4v8", start_node=v4, end_node=v8)
        #
        oev5v5 = Edge.directed("oev5v5", start_node=v5, end_node=v5)
        oev5v7 = Edge.directed("oev5v7", start_node=v5, end_node=v7)
        #
        oev6v5 = Edge.directed("oev6v5", start_node=v6, end_node=v5)
        oev6v6 = Edge.directed("oev6v6", start_node=v6, end_node=v6)
        oev6v7 = Edge.directed("oev6v7", start_node=v6, end_node=v7)
        oev6v8 = Edge.directed("oev6v8", start_node=v6, end_node=v8)
        #
        oev6v5 = Edge.directed("oev6v5", start_node=v6, end_node=v5)
        oev6v6 = Edge.directed("oev6v6", start_node=v6, end_node=v6)
        oev6v7 = Edge.directed("oev6v7", start_node=v6, end_node=v7)
        oev6v8 = Edge.directed("oev6v8", start_node=v6, end_node=v8)
        #
        oev7v5 = Edge.directed("oev7v5", start_node=v7, end_node=v5)
        oev7v7 = Edge.directed("oev7v7", start_node=v7, end_node=v7)
        #
        oev8v5 = Edge.directed("oev8v5", start_node=v8, end_node=v5)
        oev8v6 = Edge.directed("oev8v6", start_node=v8, end_node=v6)
        oev8v7 = Edge.directed("oev8v7", start_node=v8, end_node=v7)
        oev8v8 = Edge.directed("oev8v8", start_node=v8, end_node=v8)
        #
        outg = DiGraph(
            "g2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([v1, v2, v3, v4, v5, v6, v7, v8]),
            edges=set(
                [
                    oev1v1,
                    oev1v2,
                    oev1v3,
                    oev1v4,
                    oev1v5,
                    oev1v6,
                    oev1v7,
                    oev1v8,
                    oev2v1,
                    oev2v2,
                    oev2v3,
                    oev2v4,
                    oev2v5,
                    oev2v6,
                    oev2v7,
                    oev2v8,
                    oev3v1,
                    oev3v2,
                    oev3v3,
                    oev3v4,
                    oev3v5,
                    oev3v6,
                    oev3v7,
                    oev3v8,
                    oev4v5,
                    oev4v6,
                    oev4v7,
                    oev4v8,
                    oev5v5,
                    oev5v7,
                    oev6v5,
                    oev6v6,
                    oev6v7,
                    oev6v8,
                    oev6v5,
                    oev6v6,
                    oev6v7,
                    oev6v8,
                    oev7v5,
                    oev7v7,
                    oev8v5,
                    oev8v6,
                    oev8v7,
                    oev8v8,
                ]
            ),
        )
        pdb.set_trace()
        transg = ing.find_transitive_closure()
        print(transg.V)
        print(transg.E)


if __name__ == "__main__":
    unittest.main()
