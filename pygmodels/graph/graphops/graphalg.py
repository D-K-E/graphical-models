"""!
\file graphalg.py Graph algebraic operations
"""

import math
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.graph.gtype.basegraph import BaseGraph
from pygmodels.graph.gtype.edge import Edge
from pygmodels.graph.graphops.graphops import BaseGraphBoolOps
from pygmodels.graph.graphops.graphops import BaseGraphOps
from pygmodels.graph.gtype.abstractobj import (
    AbstractDiGraph,
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
    AbstractUndiGraph,
    EdgeType,
)


class BaseGraphAlgOps:
    """"""

    @staticmethod
    def plus_minus_node_edge(
        g: AbstractGraph,
        el: Union[Set[AbstractNode], Set[AbstractEdge], AbstractGraph],
        is_plus=False,
    ) -> BaseGraph:
        """!
        \brief subtraction of elements for G - v cases, see Diestel p. 4
        """
        if isinstance(el, AbstractGraph):
            if is_plus is False:
                elnodes = set(el.V)
                nodes = {n for n in g.V if n not in elnodes}
                bg = BaseGraph.based_on_node_set(edges=set(g.E), nodes=nodes)
                bg.update_data(g.data())
                return bg
            else:
                nodes = set(g.V).union(el.V)
                edges = set(g.E).union(el.E)
                bg = BaseGraph.from_edge_node_set(edges=edges, nodes=nodes)
                bg.update_data(g.data())
                return bg

        nset = all(isinstance(e, AbstractNode) for e in el)
        if nset:
            if is_plus is False:
                nodes = {n for n in g.V if n not in el}
                edges = set(g.E)
                bg = BaseGraph.based_on_node_set(edges=edges, nodes=nodes)
                bg.update_data(g.data())
                return bg
            else:
                nodes = set(g.V).union(el)
                edges = set(g.E)
                bg = BaseGraph.based_on_node_set(edges=edges, nodes=nodes)
                bg.update_data(g.data())
                return bg
        eset = all(isinstance(e, AbstractEdge) for e in el)
        if eset:
            if is_plus is False:
                edges = {e for e in g.E if e not in el}
                bg = BaseGraph.from_edge_node_set(edges=edges, nodes=set(g.V))
                bg.update_data(g.data())
                return bg
            else:
                edges = set(g.E).union(el)
                bg = BaseGraph.from_edge_node_set(edges=edges, nodes=set(g.V))
                bg.update_data(g.data())
                return bg

    @staticmethod
    def plus_minus(
        g: AbstractGraph,
        el: Union[Set[AbstractNode], Set[AbstractEdge]],
        is_plus=False,
    ) -> BaseGraph:
        """"""
        if isinstance(el, AbstractNode):
            return BaseGraphAlgOps.plus_minus_node_edge(
                g=g, el=set([el]), is_plus=is_plus
            )
        #
        if isinstance(el, AbstractEdge):
            return BaseGraphAlgOps.plus_minus_node_edge(
                g=g, el=set([el]), is_plus=is_plus
            )
        #
        if isinstance(el, (set, frozenset)):
            return BaseGraphAlgOps.plus_minus_node_edge(g=g, el=el, is_plus=is_plus)
        #
        if isinstance(el, AbstractGraph):
            return BaseGraphAlgOps.plus_minus_node_edge(g=g, el=el, is_plus=is_plus)
        raise TypeError("argument type is not compatible with operation")

    @staticmethod
    def subtract(
        g: AbstractGraph,
        el: Union[
            Set[AbstractNode],
            Set[AbstractEdge],
            AbstractEdge,
            AbstractNode,
            AbstractGraph,
        ],
    ):
        """!
        \brief subtraction of elements for G - v cases, see Diestel p. 4
        """
        return BaseGraphAlgOps.plus_minus(g=g, el=el, is_plus=False)

    @staticmethod
    def added_edge_between_if_none(
        g: AbstractGraph, n1: AbstractNode, n2: AbstractNode, is_directed: bool = False,
    ) -> BaseGraph:
        """!
        Add edge between nodes. If there are no edges in between.
        The flag is_directed specifies if the edge is directed or not
        """
        if not BaseGraphBoolOps.is_in(g, n1) or not BaseGraphBoolOps.is_in(g, n2):
            raise ValueError("one of the nodes is not present in graph")
        n1id = n1.id()
        n2id = n2.id()
        gdata = BaseGraphOps.to_edgelist(g)
        first_eset = set(gdata[n1id])
        second_eset = set(gdata[n2id])
        common_edge_ids = first_eset.intersection(second_eset)
        if len(common_edge_ids) == 0:
            # there are no edges between the nodes
            if isinstance(g, AbstractUndiGraph):
                edge = Edge.undirected(eid=str(uuid4()), start_node=n1, end_node=n2)
                return BaseGraphAlgOps.add(g, edge)
            elif isinstance(g, AbstractDiGraph):
                edge = Edge.directed(eid=str(uuid4()), start_node=n1, end_node=n2)
                return BaseGraphAlgOps.add(g, edge)
            elif is_directed is True:
                edge = Edge.directed(eid=str(uuid4()), start_node=n1, end_node=n2)
                return BaseGraphAlgOps.add(g, edge)
            elif is_directed is False:
                edge = Edge.undirected(eid=str(uuid4()), start_node=n1, end_node=n2)
                return BaseGraphAlgOps.add(g, edge)
            else:
                raise ValueError("Must specify an edge type to be added")
        else:
            # there is already an edge in between
            return g

    @staticmethod
    def add(
        g: AbstractGraph,
        el: Union[
            Set[AbstractNode],
            Set[AbstractEdge],
            AbstractNode,
            AbstractEdge,
            AbstractGraph,
        ],
    ) -> BaseGraph:
        """!
        \brief addition of elements for G + v cases, see Diestel p. 4
        """
        return BaseGraphAlgOps.plus_minus(g=g, el=el, is_plus=True)
