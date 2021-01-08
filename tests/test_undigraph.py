"""!
Test undirected graph object
"""
from gmodels.undigraph import UndiGraph
from gmodels.node import Node
from gmodels.edge import Edge, EdgeType
import unittest


class UndiGraphTest(unittest.TestCase):
    ""

    def setUp(self):
        #
        self.n1 = Node("n1", {})
        self.n2 = Node("n2", {})
        self.n3 = Node("n3", {})
        self.n4 = Node("n4", {})
        self.n5 = Node("n5", {})
        self.e1 = Edge(
            "e1", start_node=self.n1, end_node=self.n2, edge_type=EdgeType.UNDIRECTED
        )
        self.e2 = Edge(
            "e2", start_node=self.n2, end_node=self.n3, edge_type=EdgeType.UNDIRECTED
        )
        self.e3 = Edge(
            "e3", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )
        self.e4 = Edge(
            "e4", start_node=self.n1, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
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
        self.ae = Edge(
            "ae", start_node=self.a, end_node=self.e, edge_type=EdgeType.UNDIRECTED
        )
        self.ab = Edge(
            "ab", start_node=self.a, end_node=self.b, edge_type=EdgeType.UNDIRECTED
        )
        self.af = Edge(
            "af", start_node=self.a, end_node=self.f, edge_type=EdgeType.UNDIRECTED
        )
        self.be = Edge(
            "be", start_node=self.b, end_node=self.e, edge_type=EdgeType.UNDIRECTED
        )
        self.ef = Edge(
            "ef", start_node=self.e, end_node=self.f, edge_type=EdgeType.UNDIRECTED
        )
        self.de = Edge(
            "de", start_node=self.d, end_node=self.e, edge_type=EdgeType.UNDIRECTED
        )
        self.df = Edge(
            "df", start_node=self.d, end_node=self.f, edge_type=EdgeType.UNDIRECTED
        )
        self.cd = Edge(
            "cd", start_node=self.c, end_node=self.d, edge_type=EdgeType.UNDIRECTED
        )
        self.gd = Edge(
            "gd", start_node=self.g, end_node=self.d, edge_type=EdgeType.UNDIRECTED
        )
        self.bg = Edge(
            "bg", start_node=self.b, end_node=self.g, edge_type=EdgeType.UNDIRECTED
        )
        self.bc = Edge(
            "bc", start_node=self.b, end_node=self.c, edge_type=EdgeType.UNDIRECTED
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
            edges=set([self.ae, self.ab, self.af, self.be, self.ef,]),
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
            edges=set([self.ab, self.af, self.be,]),
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
            nodes=self.ugraph2.nodes().union(self.graph_2.nodes()),
            edges=self.ugraph2.edges().union(self.graph_2.edges()),
        )
        # ugraph 4
        #   +-----+     n1 -- n2 -- n3 -- n4
        #  /       \     \                /
        # a -- b -- e     +--------------+
        #  \       /
        #   +-----f

        self.e_n = Edge(
            "en", start_node=self.e, end_node=self.n1, edge_type=EdgeType.UNDIRECTED
        )

        self.ugraph5 = UndiGraph(
            "ug5",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.a, self.b, self.c, self.d, self.e, self.f, self.g]),
            edges=set(
                [self.ab, self.bc, self.bg, self.cd, self.gd, self.df, self.de, self.ef]
            ),
        )
        # ugraph 5
        #   +-----+    n1 -- n2 -- n3 -- n4
        #  /       \  /  \               /
        # a -- b -- e     +-------------+
        #  \       /
        #   +-----f

    def test_id(self):
        return self.assertEqual(self.ugraph1.id(), "ug1")

    def test_find_shortest_path(self):
        ""
        path = self.ugraph4.find_shortest_paths(n1=self.n1)
        pathl = path[2]
        lpath = [(k, v) for k, v in pathl.items() if v < float("inf")]
        lpath.sort(key=lambda x: x[1])
        nps = [x[0] for x in lpath]
        self.assertEqual(nps, ["n1", "n2", "n3", "n4"])

    def test_lower_bound_for_path_length(self):
        mdegre = self.ugraph1.lower_bound_for_path_length()
        self.assertEqual(mdegre, 0)

    def test_minimum_spanning_tree(self):
        ""
        tree = self.ugraph3.find_minimum_spanning_tree()
        leaves = tree.leaves()
        self.assertEqual(leaves, set([self.e, self.f]))

    def test_find_articulation_points(self):
        ""
        points = self.ugraph5.find_articulation_points()
        self.assertEqual(set([self.b, self.d]), points)


if __name__ == "__main__":
    unittest.main()
