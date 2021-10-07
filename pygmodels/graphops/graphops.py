"""!
\file graphops.py Graph operations implemented for BaseGraph and its subclasses
"""

import math
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.graphops.bgraphops import (
    BaseGraphBoolOps,
    BaseGraphEdgeOps,
    BaseGraphNodeOps,
    BaseGraphOps,
)
from pygmodels.gtype.abstractobj import (
    AbstractDiGraph,
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
    AbstractUndiGraph,
)
from pygmodels.gtype.basegraph import BaseGraph
from pygmodels.gtype.edge import Edge


class BaseGraphSetOps:
    """!"""

    @staticmethod
    def set_op_node_edge(
        g: AbstractGraph,
        obj: Union[Set[AbstractNode], Set[AbstractEdge]],
        op: Callable[
            [Union[Set[AbstractNode], Set[AbstractEdge]]],
            Union[Set[AbstractNode], Set[AbstractEdge]],
        ],
    ):
        """!"""
        is_eset = all(isinstance(o, AbstractEdge) for o in obj)
        if is_eset:
            edges = g.E
            return op(edges, obj)
        is_nset = all(isinstance(o, AbstractNode) for o in obj)
        if is_nset is False:
            raise TypeError(
                "argument type is not supported: " + type(obj).__name__
            )
        #
        nodes = g.V
        return op(nodes, obj)

    @staticmethod
    def set_op(
        g: AbstractGraph,
        obj: Union[
            Set[AbstractNode],
            Set[AbstractEdge],
            AbstractGraph,
            AbstractNode,
            AbstractEdge,
        ],
        op: Callable[
            [Union[Set[AbstractNode], Set[AbstractEdge]]],
            Union[Set[AbstractNode], Set[AbstractEdge], AbstractGraph],
        ],
    ) -> Optional[Union[Set[AbstractNode], Set[AbstractEdge], bool]]:
        """!
        \brief generic set operation for graph

        \param obj the hooked object to operation. We deduce its corresponding
        argument from its type.
        \param op operation that is going to be applied to obj and its
        corresponding object.

        The idea is to give a single interface for generic set operation
        functions. For example if object is a set of nodes we provide
        the target for the operation as the nodes of this graph, if it is an
        edge we provide a set of edges of this graph
        """
        is_node = isinstance(obj, AbstractNode)
        if is_node:
            return BaseGraphSetOps.set_op_node_edge(g=g, obj=set([obj]), op=op)
        is_edge = isinstance(obj, AbstractEdge)
        if is_edge:
            return BaseGraphSetOps.set_op_node_edge(g=g, obj=set([obj]), op=op)
        is_set = isinstance(obj, (set, frozenset))
        if is_set:
            return BaseGraphSetOps.set_op_node_edge(g=g, obj=obj, op=op)
        is_graph = isinstance(obj, AbstractGraph)
        if is_graph:
            oeset = BaseGraphOps.edges(obj)
            onset = BaseGraphOps.nodes(obj)
            oedge_set = BaseGraphSetOps.set_op(g, obj=oeset, op=op)
            onode_set = BaseGraphSetOps.set_op(g, obj=onset, op=op)
            gdata = g.data()
            gdata.update(obj.data())
            return BaseGraph(
                gid=str(uuid4()), nodes=onode_set, edges=oedge_set, data=gdata
            )
        else:
            raise TypeError(
                "argument type is not supported: " + type(obj).__name__
            )

    @staticmethod
    def intersection(
        g: AbstractGraph,
        aset: Union[
            Set[AbstractNode],
            Set[AbstractEdge],
            AbstractGraph,
            AbstractNode,
            AbstractEdge,
        ],
    ) -> Union[Set[AbstractNode], Set[AbstractEdge], AbstractGraph]:
        """!
        \brief obtain intersection of either node or edge set
        """
        return BaseGraphSetOps.set_op(
            g, obj=aset, op=lambda gset, y: gset.intersection(y)
        )

    @staticmethod
    def union(
        g: AbstractGraph,
        aset: Union[
            Set[AbstractNode],
            Set[AbstractEdge],
            AbstractGraph,
            AbstractEdge,
            AbstractNode,
        ],
    ) -> Union[Set[AbstractNode], Set[AbstractEdge], AbstractGraph]:
        """!
        \brief obtain union of either node or edge set
        """
        return BaseGraphSetOps.set_op(
            g, obj=aset, op=lambda gset, y: gset.union(y)
        )

    @staticmethod
    def difference(
        g: AbstractGraph,
        aset: Union[
            Set[AbstractNode],
            Set[AbstractEdge],
            AbstractGraph,
            AbstractEdge,
            AbstractNode,
        ],
    ) -> Union[Set[AbstractNode], Set[AbstractEdge], AbstractGraph]:
        """!
        \brief obtain set difference of either node or edge set
        """
        return BaseGraphSetOps.set_op(
            g, obj=aset, op=lambda gset, y: gset.difference(y)
        )

    @staticmethod
    def symmetric_difference(
        g: AbstractGraph,
        aset: Union[
            Set[AbstractNode],
            Set[AbstractEdge],
            AbstractGraph,
            AbstractNode,
            AbstractEdge,
        ],
    ) -> Union[Set[AbstractNode], Set[AbstractEdge], AbstractGraph]:
        """!
        \brief obtain symmetric set difference of either node or edge set.
        """
        return BaseGraphSetOps.set_op(
            g, obj=aset, op=lambda gset, y: gset.symmetric_difference(y)
        )

    @staticmethod
    def contains(
        g: AbstractGraph,
        a: Union[
            Set[AbstractEdge],
            Set[AbstractNode],
            AbstractGraph,
            AbstractNode,
            AbstractEdge,
        ],
    ) -> bool:
        """!
        \brief check if argument set of nodes or edges is contained by graph
        """
        return BaseGraphSetOps.set_op(
            g, obj=a, op=lambda gset, y: y.issubset(gset) is True
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
            return BaseGraphAlgOps.plus_minus_node_edge(
                g=g, el=el, is_plus=is_plus
            )
        #
        if isinstance(el, AbstractGraph):
            return BaseGraphAlgOps.plus_minus_node_edge(
                g=g, el=el, is_plus=is_plus
            )
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
        g: AbstractGraph,
        n1: AbstractNode,
        n2: AbstractNode,
        is_directed: bool = False,
    ) -> BaseGraph:
        """!
        Add edge between nodes. If there are no edges in between.
        The flag is_directed specifies if the edge is directed or not
        """
        if not BaseGraphBoolOps.is_in(g, n1) or not BaseGraphBoolOps.is_in(
            g, n2
        ):
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
                edge = Edge.undirected(
                    eid=str(uuid4()), start_node=n1, end_node=n2
                )
                return BaseGraphAlgOps.add(g, edge)
            elif isinstance(g, AbstractDiGraph):
                edge = Edge.directed(
                    eid=str(uuid4()), start_node=n1, end_node=n2
                )
                return BaseGraphAlgOps.add(g, edge)
            elif is_directed is True:
                edge = Edge.directed(
                    eid=str(uuid4()), start_node=n1, end_node=n2
                )
                return BaseGraphAlgOps.add(g, edge)
            elif is_directed is False:
                edge = Edge.undirected(
                    eid=str(uuid4()), start_node=n1, end_node=n2
                )
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
