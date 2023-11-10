"""!
Test undirected graph object
"""
import unittest
from random import choice

from pygmodels.graph.graphmodel.undigraph import UndiGraph
from pygmodels.graph.graphops.graphops import BaseGraphOps
from pygmodels.graph.graphtype.edge import Edge, EdgeType
from pygmodels.graph.graphtype.node import Node


class UndiGraphTest(unittest.TestCase):
    """"""

    def setUp(self):
        #
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
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
            start_node=self.n1,
            end_node=self.n4,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.graph_2 = UndiGraph(
            "g2",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2, self.e3]),
        )

        self.a = Node("a", {})  # b
        self.b = Node("b", {})  # c
        self.c = Node("c", {})
        self.d = Node("d", {})
        self.f = Node("f", {})  # d
        self.e = Node("e", {})  # e
        self.g = Node("g", {})
        self.h = Node("h", {})
        self.ae = Edge(
            "ae",
            start_node=self.a,
            end_node=self.e,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.ab = Edge(
            "ab",
            start_node=self.a,
            end_node=self.b,
            data={"w": 1},
            edge_type=EdgeType.UNDIRECTED,
        )
        self.af = Edge(
            "af",
            start_node=self.a,
            end_node=self.f,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.ah = Edge(
            "ah",
            start_node=self.a,
            end_node=self.h,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.bh = Edge(
            "bh",
            start_node=self.b,
            end_node=self.h,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.be = Edge(
            "be",
            start_node=self.b,
            end_node=self.e,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.ef = Edge(
            "ef",
            data={"w": 5},
            start_node=self.e,
            end_node=self.f,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.de = Edge(
            "de",
            data={"w": 4},
            start_node=self.d,
            end_node=self.e,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.df = Edge(
            "df",
            data={"w": 8},
            start_node=self.d,
            end_node=self.f,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.cd = Edge(
            "cd",
            data={"w": 3},
            start_node=self.c,
            end_node=self.d,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.cg = Edge(
            "cg",
            start_node=self.c,
            end_node=self.g,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.gd = Edge(
            "gd",
            data={"w": 7},
            start_node=self.g,
            end_node=self.d,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.bg = Edge(
            "bg",
            data={"w": 6},
            start_node=self.b,
            end_node=self.g,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.fg = Edge(
            "fg",
            start_node=self.f,
            end_node=self.g,
            edge_type=EdgeType.UNDIRECTED,
        )
        self.bc = Edge(
            "bc",
            start_node=self.b,
            end_node=self.c,
            data={"w": 2},
            edge_type=EdgeType.UNDIRECTED,
        )

        # undirected graph
        self.ugraph1 = UndiGraph(
            "ug1",
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
        # ugraph1:
        #   +-----+
        #  /       \
        # a    b    e
        #  \       /
        #   +-----f

        self.ugraph2 = UndiGraph(
            "ug2",
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
        # ugraph2 :
        #   +-----+
        #  /       \
        # a -- b -- e
        #  \       /
        #   +-----f

        self.ugraph3 = UndiGraph(
            "ug3",
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
        # ugraph3 :
        #
        #
        # a -- b -- e
        #  \
        #   +-----f

        self.ugraph4 = UndiGraph(
            "ug4",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set(self.ugraph2.V).union(self.graph_2.V),
            edges=set(self.ugraph2.E).union(self.graph_2.E),
        )
        # ugraph 4
        #   +-----+     n1 -- n2 -- n3 -- n4
        #  /       \     \                /
        # a -- b -- e     +--------------+
        #  \       /
        #   +-----f

        self.ugraph5 = UndiGraph(
            "ug5",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set(
                [self.a, self.b, self.c, self.d, self.e, self.f, self.g]
            ),
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
        # ugraph 5
        #        +----c---+   +--e
        #       /  2     3 \ / 4 |
        # a --- b           d    | 5
        #    1   \ 6     7 / \ 8 |
        #         +---g---+   +--f

        self.ugraph6 = UndiGraph(
            "ug6",
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
        # ugraph 6
        # a--+   e----d
        # |   \      / \
        # |    b----c   f
        # |   /      \ /
        # h--+        g
        self.ad = Edge(
            "ad",
            start_node=self.a,
            end_node=self.d,
            edge_type=EdgeType.UNDIRECTED,
        )
        #
        self.ugraph7 = UndiGraph(
            "ug7",
            nodes=set([self.a, self.b, self.c, self.d]),
            edges=set([self.ab, self.bc, self.cd, self.ad]),
        )
        # ugraph7
        #     a
        #    / \
        #   d   b
        #    \ /
        #     c

    def test_id(self):
        return self.assertEqual(self.ugraph1.id(), "ug1")

    def test_find_shortest_path(self):
        """"""
        path_props = self.ugraph4.find_shortest_paths(n1=self.n1)
        pathl = path_props.top_sort
        lpath = [(k, v) for k, v in pathl.items() if v < float("inf")]
        lpath.sort(key=lambda x: x[1])
        nps = [x[0] for x in lpath]
        self.assertEqual(nps, ["n1", "n2", "n3", "n4"])

    def test_lower_bound_for_path_length(self):
        mdegre = self.ugraph1.lower_bound_for_path_length()
        self.assertEqual(mdegre, 0)

    def test_minimum_spanning_tree(self):
        """"""
        tree, L = self.ugraph5.find_minimum_spanning_tree(
            weight_fn=lambda e: e.data()["w"]
        )

        self.assertEqual(
            [li.id() for li in L],
            ["ab", "bc", "cd", "de", "ef", "bg", "gd", "df"],
        )

    def test_maximum_spanning_tree(self):
        """"""
        tree, L = self.ugraph5.find_maximum_spanning_tree(
            weight_fn=lambda e: e.data()["w"]
        )
        self.assertEqual(
            [li.id() for li in L],
            ["df", "gd", "bg", "ef", "de", "cd", "bc", "ab"],
        )

    def test_find_articulation_points(self):
        """"""
        points = self.ugraph5.find_articulation_points()
        self.assertEqual(set([self.b, self.d]), points)

    def test_find_bridges(self):
        """
        Test taken from Erciyes p. 235, Fig. 8.5
        """
        bridges = self.ugraph6.find_bridges()
        self.assertEqual(bridges, set([self.de, self.bc]))

    def test_find_maximal_cliques(self):
        """!"""
        cliques = self.ugraph7.find_maximal_cliques()
        compare = [
            set([self.a, self.b]),
            set([self.b, self.c]),
            set([self.a, self.d]),
            set([self.c, self.d]),
        ]
        for c in compare:
            indx = cliques.index(c)
            cliques.pop(indx)
        self.assertEqual(cliques, [])


if __name__ == "__main__":
    unittest.main()
