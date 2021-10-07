"""!
\file digraphops.py Directed Graph Operations

Basically an operation class for managing edge/node related operations
involving directed edges
"""

from pygmodels.gtype.abstractobj import EdgeType
from pygmodels.gtype.abstractobj import AbstractDiGraph
from pygmodels.gtype.abstractobj import AbstractNode
from pygmodels.gtype.abstractobj import AbstractEdge
from pygmodels.graphops.bgraphops import BaseGraphBoolOps
from typing import Set, Callable


class DiGraphBoolOps:
    """!
    Operations that result in booleans with directed graphs
    """

    @staticmethod
    def is_family_of(g: AbstractDiGraph, src: AbstractNode, dst: AbstractNode) -> bool:
        """!
        \brief Check if src is family of dst

        \todo What if the graph has self loops. What if src and dst are same
        nodes.

        Checks two positional conditions with respect to nodes.
        This function can also be implemented as a one liner with something
        like:
        \code
        return self.is_parent_of(n1,n2) or self.is_child_of(n1,n2)
        \endcode
        The current implementation is a little more efficient than that. There
        is also a room for improvement, since it can be much more efficient
        using edge list representation.
        """
        for e in g.E:
            # dst is child of src
            child_cond = e.start() == src and e.end() == dst
            # dst is parent of src
            parent_cond = e.start() == dst and e.end() == src
            if child_cond or parent_cond:
                return True
        return False

    @staticmethod
    def is_parent_of(
        g: AbstractDiGraph, parent: AbstractNode, child: AbstractNode
    ) -> bool:
        """!
        \brief check if one node is parent of another node

        We define the notion of parent node as the following.
        For all e in E[G] and for all {v,w} in V[e] if e is an outgoing edge of
        v and incoming edge of w than v is parent of w.
        """

        def cond(n_1: AbstractNode, n_2: AbstractNode, e: AbstractEdge):
            """"""
            c = n_1 == e.start() and e.end() == n_2
            return c

        return BaseGraphBoolOps.is_related_to(g, n1=parent, n2=child, condition=cond)

    @staticmethod
    def is_child_of(
        g: AbstractDiGraph, child: AbstractNode, parent: AbstractNode
    ) -> bool:
        """!
        \brief  check if one node is child of another node

        We define the notion of child node as the following.
        For all e in E[G] and for all {v,w} in V[e] if e is an incoming edge of
        v and outgoing edge of w than v is child of w.
        As you can see from the definition provided in is_parent_of() as well,
        if v is child of w, then w is parent of v.
        """
        return DiGraphBoolOps.is_parent_of(g, parent=parent, child=child)

    @staticmethod
    def is_adjacent_of(g: AbstractDiGraph, e1: AbstractEdge, e2: AbstractEdge) -> bool:
        """!
        \brief check if edges have a common node
        """
        if not BaseGraphBoolOps.is_in(self, e1) or not BaseGraphBoolOps.is_in(self, e2):
            raise ValueError("argument edges are not in graph")

        n1_ids = e1.node_ids()
        n2_ids = e2.node_ids()
        return len(n1_ids.intersection(n2_ids)) > 0


class DiGraphNumericOps:
    """!
    Operations that result in numeric results involving directed graphs
    """

    @staticmethod
    def in_degree_of(g: AbstractDiGraph, n: AbstractNode) -> int:
        return len(DiGraphNodeOps.parents_of(g, n))

    @staticmethod
    def out_degree_of(g: AbstractDiGraph, n: AbstractNode) -> int:
        return len(DiGraphNodeOps.children_of(g, n))


class DiGraphEdgeOps:
    """!
    Operations that result in edge or set of edges with directed graphs
    """

    @staticmethod
    def edge_by_vertices(
        g: AbstractDiGraph, start: AbstractNode, end: AbstractNode
    ) -> Set[AbstractEdge]:
        """!
        \brief obtain edge by using its start and end node.

        \throws ValueError If any of the arguments are not found in this graph we
        throw value error.
        """
        if not BaseGraphBoolOps.is_in(self, start) or not BaseGraphBoolOps.is_in(
            self, end
        ):
            raise ValueError("argument nodes are not in graph")
        #
        eset: Set[Edge] = set()
        for e in g.E:
            if e.start().id() == start.id() and e.end().id() == end.id():
                eset.add(e)
        return eset


class DiGraphNodeOps:
    """!
    Operations that result in node or set of nodes with directed graphs
    """

    @staticmethod
    def family_set_of(
        g: AbstractDiGraph,
        n: AbstractNode,
        fcond: Callable[[AbstractEdge, AbstractNode], bool],
        enode_fn: Callable[[AbstractEdge], AbstractNode],
    ):
        """!
        \brief obtain direct family set of nodes from given argument

        \param n argument node whose family set, we are interested in
        \param fcond family condition function
        \param enode_fn node extracting function. Extracts node from given edge

        \throws ValueError if the argument does not belong to this graph we
        throw value error.
        """
        if not BaseGraphBoolOps.is_in(g, n):
            raise ValueError("node not in graph")
        family = set()
        for e in g.E:
            if fcond(e, n) is True:
                family.add(enode_fn(e))
        return family

    def children_of(g: AbstractDiGraph, n: AbstractNode) -> Set[AbstractNode]:
        """!
        \brief obtain direct child set of nodes from given argument

        \throws ValueError if the argument does not belong to this graph we
        throw value error.
        """
        return DiGraphNodeOps.family_set_of(
            g=g,
            n=n,
            fcond=lambda e, node: e.start().id() == node.id(),
            enode_fn=lambda e: e.end(),
        )

    def parents_of(g: AbstractDiGraph, n: AbstractNode) -> Set[AbstractNode]:
        """!
        \brief obtain direct parent set of nodes from given argument

        \throws ValueError if the argument does not belong to this graph we
        throw value error.
        """
        return DiGraphNodeOps.family_set_of(
            g=g,
            n=n,
            fcond=lambda e, node: e.end().id() == node.id(),
            enode_fn=lambda e: e.start(),
        )
