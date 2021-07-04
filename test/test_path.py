"""!
Test path object
"""
from gmodels.gtype.path import Path
from gmodels.gtype.graph import Graph
from gmodels.gtype.node import Node
from gmodels.gtype.edge import Edge, EdgeType
import unittest


class PathTest(unittest.TestCase):
    ""

    def setUp(self):
        self.n1 = Node("a", {})  # b
        self.n2 = Node("b", {})  # c
        self.n3 = Node("f", {})  # d
        self.n4 = Node("e", {})  # e
        self.e1 = Edge(
            "e1", start_node=self.n1, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )
        self.e2 = Edge(
            "e2", start_node=self.n1, end_node=self.n2, edge_type=EdgeType.UNDIRECTED
        )
        self.e3 = Edge(
            "e3", start_node=self.n1, end_node=self.n3, edge_type=EdgeType.UNDIRECTED
        )
        self.e4 = Edge(
            "e4", start_node=self.n2, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )
        self.e5 = Edge(
            "e5", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.UNDIRECTED
        )

        # undirected graph
        self.ugraph = Graph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e1, self.e2, self.e3, self.e4, self.e5]),
        )

        # make some directed edges
        self.e6 = Edge(
            "e6", start_node=self.n1, end_node=self.n3, edge_type=EdgeType.DIRECTED
        )
        self.e7 = Edge(
            "e7", start_node=self.n3, end_node=self.n2, edge_type=EdgeType.DIRECTED
        )
        self.e8 = Edge(
            "e8", start_node=self.n3, end_node=self.n4, edge_type=EdgeType.DIRECTED
        )
        self.e9 = Edge(
            "e9", start_node=self.n4, end_node=self.n2, edge_type=EdgeType.DIRECTED
        )
        self.e10 = Edge(
            "e10", start_node=self.n4, end_node=self.n1, edge_type=EdgeType.DIRECTED
        )
        self.dgraph = Graph(
            "g1",
            data={"my": "graph", "data": "is", "very": "awesome"},
            nodes=set([self.n1, self.n2, self.n3, self.n4]),
            edges=set([self.e6, self.e7, self.e8, self.e9, self.e10]),
        )
        self.path = Path(gid="mpath", data={}, edges=[self.e2, self.e4, self.e5],)
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
        ""
        plen = self.path.length()
        self.assertEqual(3, plen)

    def test_node_list(self):
        ""
        nlist = self.path.node_list()
        self.assertEqual(nlist, [self.n1, self.n2, self.n4])

    def test_node_list_f(self):
        ""
        nlist = self.path.node_list()
        self.assertFalse(nlist == [self.n2, self.n1, self.n4])

    def test_endvertices(self):
        ""
        nlist = self.path.endvertices()
        self.assertEqual(nlist, (self.n1, self.n4))

    def test_uniform_cost_search(self):
        ""
        start_node = self.b
        goal_node = self.m
        problem_set = self.gtree.edges()
        solution = Path.uniform_cost_search(
            goal=goal_node, start=start_node, problem_set=problem_set
        )
        edges = [solution["edge"]]
        while solution["parent"] is not None:
            solution = solution["parent"]
            edges.append(solution["edge"])
        edges.pop()  # last element edge is None
        self.assertEqual(list(reversed(edges)), [self.bf, self.fm])

    def test_from_ucs(self):
        ""
        start_node = self.b
        goal_node = self.m
        problem_set = self.gtree.edges()
        p = Path.from_ucs(goal=goal_node, start=start_node, problem_set=problem_set)
        self.assertEqual(p.node_list(), [self.b, self.f, self.m])


if __name__ == "__main__":
    unittest.main()
