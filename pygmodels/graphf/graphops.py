"""!
\file graphops.py Graph operations implemented for BaseGraph and its subclasses
"""

from typing import Set, Optional, Callable, List, Tuple, Union, Dict, FrozenSet
from pygmodels.gtype.abstractobj import AbstractGraph, AbstractUndiGraph
from pygmodels.gtype.abstractobj import AbstractGraph, AbstractDiGraph
from pygmodels.gtype.abstractobj import AbstractNode, AbstractEdge
from pygmodels.gtype.basegraph import BaseGraph
from pygmodels.graphf.bgraphops import BaseGraphOps
from pygmodels.gtype.edge import Edge
from uuid import uuid4
import math


class BaseGraphSetOps:
    """!
    """

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
        is_edge = isinstance(obj, AbstractEdge)
        is_graph = isinstance(obj, AbstractGraph)
        is_set = isinstance(obj, (set, frozenset))
        is_eset = False
        is_nset = False
        if is_set:
            is_eset = all(isinstance(o, AbstractEdge) for o in obj)
            if is_eset is False:
                is_nset = all(isinstance(o, AbstractNode) for o in obj)
                if is_nset is False:
                    raise TypeError(
                        "argument type is not supported: " + type(obj).__name__
                    )
        aset = set()
        if is_node:
            aset.add(obj)
            return op(BaseGraphOps.nodes(g), aset)
        elif is_edge:
            aset.add(obj)
            return op(BaseGraphOps.edges(g), aset)
        if is_set:
            aset = obj
        if is_eset:
            return op(BaseGraphOps.edges(g), aset)
        elif is_nset:
            return op(BaseGraphOps.nodes(g), aset)
        elif is_graph:
            oeset = BaseGraphOps.edges(obj)
            onset = BaseGraphOps.nodes(obj)
            oedge_set = BaseGraphSetOps.set_op(g, obj=oeset, op=op)
            onode_set = BaseGraphSetOps.set_op(g, obj=onset, op=op)
            return BaseGraph(
                gid=str(uuid4()),
                nodes=onode_set,
                edges=oedge_set,
                data=g.data().update(obj.data()),
            )
        else:
            raise TypeError("argument type is not supported: " + type(obj).__name__)

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
        return BaseGraphSetOps.set_op(g, obj=aset, op=lambda gset, y: gset.union(y))

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
    ""

    @staticmethod
    def subtract(
        g: AbstractGraph,
        el: Union[
            Set[AbstractNode],
            Set[AbstractEdge],
            AbstractNode,
            AbstractEdge,
            AbstractGraph,
        ],
    ) -> BaseGraph:
        ""
        #
        res = BaseGraphSetOps.difference(g, el)
        if isinstance(res, AbstractGraph):
            return res
        if isinstance(res, (set, frozenset)):
            if all(isinstance(r, AbstractNode) for r in res):
                # delete vertices that contained the deleted node
                rV = {r.id(): r for r in res}
                edges = set()
                for edge in g.E.values():
                    nids = edge.node_ids()
                    if all(n in rV for n in nids):
                        edges.add(edge)
                return BaseGraph(
                    gid=str(uuid4()), nodes=res, edges=edges, data=g.data(),
                )
            if all(isinstance(r, AbstractEdge) for r in res):
                return BaseGraph(
                    gid=str(uuid4()), nodes=set(g.V.values()), edges=res, data=g.data()
                )

    @staticmethod
    def added_edge_between_if_none(
        g: AbstractGraph, n1: AbstractNode, n2: AbstractNode, is_directed: bool = False
    ) -> BaseGraph:
        """!
        Add edge between nodes. If there are no edges in between.
        The flag is_directed specifies if the edge is directed or not
        """
        if not BaseGraphOps.is_in(g, n1) or not BaseGraphOps.is_in(g, n2):
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
        el: Union[Set[AbstractNode], Set[AbstractEdge], AbstractNode, AbstractEdge],
    ) -> BaseGraph:
        ""
        #
        res = BaseGraphSetOps.union(g, el)
        if isinstance(res, AbstractGraph):
            return res
        if isinstance(res, (set, frozenset)):
            if all(isinstance(r, AbstractNode) for r in res):
                return BaseGraph(
                    gid=str(uuid4()), nodes=res, edges=set(g.E.values()), data=g.data()
                )
            if all(isinstance(r, AbstractEdge) for r in res):
                return BaseGraph(
                    gid=str(uuid4()), nodes=set(g.V.values()), edges=res, data=g.data()
                )
