"""!
Tests our graph search algorithms
"""
import cProfile
import unittest

# profiler related
from pstats import Stats

from pygmodels.graph.graphops.graphops import BaseGraphOps
from pygmodels.graph.graphops.graphsearcher import BaseGraphSearcher
from pygmodels.graph.graphtype.basegraph import BaseGraph
from pygmodels.graph.graphtype.edge import Edge, EdgeType
from pygmodels.graph.graphtype.node import Node


class BaseGraphSearcherTests(unittest.TestCase):
    """"""

    def setUp(self):
        self.verbose = False
        #
        # Alan Gibbons, Algorithmic graph theory 1985, p. 22, fig. 1.16
        # depth first undirected graph

        # nodes
        self.n1 = Node("n1", data={})
        self.n2 = Node("n2", data={})
        self.n3 = Node("n3", data={})
        self.n4 = Node("n4", data={})
        self.n5 = Node("n5", data={})
        self.n6 = Node("n6", data={})
        self.n7 = Node("n7", data={})
        self.n8 = Node("n8", data={})
        self.n9 = Node("n9", data={})
        self.n10 = Node("n10", data={})
        self.n11 = Node("n11", data={})
        self.n12 = Node("n12", data={})
        self.n13 = Node("n13", data={})

        # edges
        self.e1u = Edge.undirected(
            "n1n4", start_node=self.n1, end_node=self.n4, data={}
        )
        self.e2u = Edge.undirected(
            "n1n3", start_node=self.n1, end_node=self.n3, data={}
        )
        self.e3u = Edge.undirected(
            "n1n2", start_node=self.n1, end_node=self.n2, data={}
        )
        self.e4u = Edge.undirected(
            "n1n5", start_node=self.n1, end_node=self.n5, data={}
        )
        self.e5u = Edge.undirected(
            "n1n6", start_node=self.n1, end_node=self.n6, data={}
        )
        self.e6u = Edge.undirected(
            "n1n7", start_node=self.n1, end_node=self.n7, data={}
        )
        self.e7u = Edge.undirected(
            "n1n8", start_node=self.n1, end_node=self.n8, data={}
        )
        self.e8u = Edge.undirected(
            "n8n2", start_node=self.n8, end_node=self.n2, data={}
        )
        self.e9u = Edge.undirected(
            "n9n10", start_node=self.n9, end_node=self.n10, data={}
        )
        self.e10u = Edge.undirected(
            "n9n13", start_node=self.n9, end_node=self.n13, data={}
        )
        self.e11u = Edge.undirected(
            "n10n11", start_node=self.n10, end_node=self.n11, data={}
        )
        self.e12u = Edge.undirected(
            "n10n12", start_node=self.n10, end_node=self.n12, data={}
        )
        self.ugraph = BaseGraph(
            "ugraph",
            nodes=set(
                [
                    self.n1,
                    self.n2,
                    self.n3,
                    self.n4,
                    self.n5,
                    self.n6,
                    self.n7,
                    self.n8,
                    self.n9,
                    self.n10,
                    self.n11,
                    self.n12,
                    self.n13,
                ]
            ),
            edges=set(
                [
                    self.e1u,
                    self.e2u,
                    self.e3u,
                    self.e4u,
                    self.e5u,
                    self.e6u,
                    self.e7u,
                    self.e8u,
                    self.e9u,
                    self.e10u,
                    self.e11u,
                    self.e12u,
                ]
            ),
            data={},
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
        self.gtree = BaseGraph.from_edgeset(
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

        # initialize profiler
        self.prof = cProfile.Profile()
        self.prof.enable()
        # print("\n<<<<--------")

    def tearDown(self):
        """ """
        p = Stats(self.prof)
        p.sort_stats("cumtime")
        if self.verbose is True:
            p.dump_stats("profiles/test_graphsearcher.py.prof")
            p.print_stats()
        p.strip_dirs()
        # p.print_stats()
        # print("\n--------->>>")

    def test_id(self):
        return self.assertEqual(self.ugraph.id(), "ugraph")

    @unittest.skip("Implementation is not finished yet")
    def test_depth_first_search(self):
        """"""

        def egen(node):
            return BaseGraphOps.edges_of(self.ugraph, node)

        result = BaseGraphSearcher.depth_first_search(
            g=self.ugraph, edge_generator=egen
        )
        self.assertEqual(2, result["nb-component"])
        # test leaves
        preds = result["dfs-trees"]
        comps = []
        for root, c in preds.items():
            cd = {}
            for key, val in c.items():
                if val is not None:
                    cd[key] = val
            comps.append(cd)
        # print(comps)
        first = comps.pop(0)

    def test_uniform_cost_search(self):
        """"""
        start_node = self.b
        goal_node = self.m
        problem_set = self.gtree.E
        elist, solution = BaseGraphSearcher.uniform_cost_search(
            g=self.gtree,
            goal=goal_node,
            start=start_node,
            problem_set=problem_set,
        )
        edges = [solution["edge"]]
        while solution["parent"] is not None:
            solution = solution["parent"]
            edges.append(solution["edge"])
        edges.pop()  # last element edge is None
        self.assertEqual(list(reversed(edges)), [self.bf, self.fm])
