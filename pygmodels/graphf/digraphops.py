"""!
\file digraphops.py Directed Graph Operations

Basically an operation class for managing edge/node related operations
involving directed edges
"""

from pygmodels.gtype.abstractobj import EdgeType
from pygmodels.gtype.abstractobj import AbstractDiGraph
from pygmodels.gtype.abstractobj import AbstractNode
from pygmodels.gtype.abstractobj import AbstractEdge
from pygmodels.graphf.bgraphops import BaseGraphBoolOps


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

        def cond(n_1: Node, n_2: Node, e: Edge):
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
