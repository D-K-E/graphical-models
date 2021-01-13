"""!
Test directed graph object
"""
from gmodels.gtypes.digraph import DiGraph
from gmodels.gtypes.node import Node
from gmodels.gtypes.edge import Edge, EdgeType
import unittest
import pprint


class DiGraphTest(unittest.TestCase):
    ""

    def setUp(self):
        #
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
        self.e1 = Edge(
            "e1", start_node=self.n1, end_node=self.n2, edge_type=EdgeType.DIRECTED
        )
        self.e2 = Edge(
            "e2", start_node=self.n2, end_node=self.n3, edge_type=EdgeType.DIRECTED
        )
        self.e3 = Edge(
            "e3", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.DIRECTED
        )
        self.e4 = Edge(
            "e4", start_node=self.n1, end_node=self.n4, edge_type=EdgeType.DIRECTED
        )
        self.graph_2 = DiGraph(
            "g2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2, self.e3]),
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
        self.ae = Edge(
            "ae", start_node=self.a, end_node=self.e, edge_type=EdgeType.DIRECTED
        )
        self.ab = Edge(
            "ab", start_node=self.a, end_node=self.b, edge_type=EdgeType.DIRECTED
        )
        self.af = Edge(
            "af", start_node=self.a, end_node=self.f, edge_type=EdgeType.DIRECTED
        )
        self.ah = Edge(
            "ah", start_node=self.a, end_node=self.h, edge_type=EdgeType.DIRECTED
        )
        self.bh = Edge(
            "bh", start_node=self.b, end_node=self.h, edge_type=EdgeType.DIRECTED
        )
        self.be = Edge(
            "be", start_node=self.b, end_node=self.e, edge_type=EdgeType.DIRECTED
        )
        self.ef = Edge(
            "ef", start_node=self.e, end_node=self.f, edge_type=EdgeType.DIRECTED
        )
        self.de = Edge(
            "de", start_node=self.d, end_node=self.e, edge_type=EdgeType.DIRECTED
        )
        self.df = Edge(
            "df", start_node=self.d, end_node=self.f, edge_type=EdgeType.DIRECTED
        )
        self.cd = Edge(
            "cd", start_node=self.c, end_node=self.d, edge_type=EdgeType.DIRECTED
        )
        self.cg = Edge(
            "cg", start_node=self.c, end_node=self.g, edge_type=EdgeType.DIRECTED
        )
        self.gd = Edge(
            "gd", start_node=self.g, end_node=self.d, edge_type=EdgeType.DIRECTED
        )
        self.bg = Edge(
            "bg", start_node=self.b, end_node=self.g, edge_type=EdgeType.DIRECTED
        )
        self.fg = Edge(
            "fg", start_node=self.f, end_node=self.g, edge_type=EdgeType.DIRECTED
        )
        self.bc = Edge(
            "bc", start_node=self.b, end_node=self.c, edge_type=EdgeType.DIRECTED
        )

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
            edges=set([self.ae, self.ab, self.af, self.be, self.ef,]),
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
            edges=set([self.ab, self.af, self.be,]),
        )
        # dgraph3 :
        #
        # a -> b -> e
        #  \
        #   +---> f

        self.dgraph4 = DiGraph(
            "dg4",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=self.dgraph2.nodes().union(self.graph_2.nodes()),
            edges=self.dgraph2.edges().union(self.graph_2.edges()),
        )
        # dgraph 4
        #
        # a -> b -> e -> f   n1 -> n2 -> n3 -> n4
        # |         ↑    ↑   |                  ↑
        # +---------+----+   +------------------+

        self.e_n = Edge(
            "en", start_node=self.e, end_node=self.n1, edge_type=EdgeType.DIRECTED
        )

        self.dgraph5 = DiGraph(
            "dg5",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.c, self.d, self.e, self.f, self.g]),
            edges=set(
                [self.ab, self.bc, self.bg, self.cd, self.gd, self.df, self.de, self.ef]
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
            nodes=set([self.a, self.b, self.c, self.d, self.e, self.f, self.g, self.h]),
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
        return self.assertEqual(self.dgraph1.id(), "dg1")

    def test_find_shortest_path(self):
        ""
        path_props = self.dgraph4.find_shortest_paths(n=self.n1)
        self.assertEqual(
            path_props["path-set"], set([self.n1, self.n2, self.n3, self.n4])
        )

    def test_check_for_path_false(self):
        v = self.dgraph4.check_for_path(self.n1, self.a)
        self.assertFalse(v)

    def test_check_for_path_true(self):
        v = self.dgraph4.check_for_path(self.n1, self.n2)
        self.assertTrue(v)

    def test_in_degree_of(self):
        v = self.dgraph6.in_degree_of(self.a)
        self.assertEqual(v, 0)

    def test_out_degree_of(self):
        v = self.dgraph6.out_degree_of(self.a)
        self.assertEqual(v, 2)

    def test_is_parent_of_t(self):
        v = self.dgraph6.is_parent_of(self.a, self.h)
        self.assertEqual(v, True)

    def test_is_parent_of_f(self):
        v = self.dgraph6.is_parent_of(self.a, self.c)
        self.assertEqual(v, False)

    def test_is_child_of_t(self):
        v = self.dgraph6.is_child_of(self.h, self.a)
        self.assertEqual(v, True)

    def test_is_child_of_f(self):
        v = self.dgraph6.is_parent_of(self.a, self.c)
        self.assertEqual(v, False)

    def test_children_of(self):
        vs = self.dgraph6.children_of(self.a)
        self.assertEqual(vs, set([self.h, self.b]))

    def test_parents_of(self):
        vs = self.dgraph6.parents_of(self.g)
        self.assertEqual(vs, set([self.c, self.f]))


if __name__ == "__main__":
    unittest.main()
