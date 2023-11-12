"""!
\file test_digraphops.py Test DiGraph operation objects
"""
import math
import unittest
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.graph.graphmodel.digraph import DiGraph
from pygmodels.graph.graphfunc.digraphops import (
    DiGraphBoolOps,
    DiGraphEdgeOps,
    DiGraphNodeOps,
    DiGraphNumericOps,
)
from pygmodels.graph.graphfunc.graphops import BaseGraphEdgeOps
from pygmodels.graph.graphtype.abstractobj import (
    AbstractDiGraph,
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
    AbstractUndiGraph,
)
from pygmodels.graph.graphtype.basegraph import BaseGraph
from pygmodels.graph.graphtype.edge import Edge, EdgeType
from pygmodels.graph.graphtype.node import Node


class DiGraphOpsTest(unittest.TestCase):
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
        return self.assertEqual(self.dgraph1.id(), "dg1")

    def test_in_degree_of(self):
        v = DiGraphNumericOps.in_degree_of(g=self.dgraph6, n=self.a)
        self.assertEqual(v, 0)

    def test_out_degree_of(self):
        v = DiGraphNumericOps.out_degree_of(g=self.dgraph6, n=self.a)
        self.assertEqual(v, 2)

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

    def test_is_parent_of_t(self):
        v = DiGraphBoolOps.is_parent_of(self.dgraph6, self.a, self.h)
        self.assertEqual(v, True)

    def test_is_parent_of_f(self):
        v = DiGraphBoolOps.is_parent_of(self.dgraph6, self.a, self.c)
        self.assertEqual(v, False)

    def test_is_child_of_t(self):
        v = DiGraphBoolOps.is_child_of(self.dgraph6, self.h, self.a)
        self.assertEqual(v, True)

    def test_is_child_of_f(self):
        v = DiGraphBoolOps.is_parent_of(self.dgraph6, self.a, self.c)
        self.assertEqual(v, False)

    def test_children_of(self):
        vs = DiGraphNodeOps.children_of(self.dgraph6, self.a)
        self.assertEqual(vs, set([self.h, self.b]))

    def test_parents_of(self):
        vs = DiGraphNodeOps.parents_of(self.dgraph6, self.g)
        self.assertEqual(vs, set([self.c, self.f]))
