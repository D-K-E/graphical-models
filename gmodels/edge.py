"""!
\file edge.py
\ingroup graphgroup Edge in a graph

\see \link graphgroup Graph Object \endlink
For more theoretical information on edges \ref edgepage
"""
from typing import Set
from gmodels.abstractobj import AbstractEdge, EdgeType
from gmodels.node import Node
from gmodels.graphobj import GraphObject


class Edge(AbstractEdge, GraphObject):
    """!
    \brief Edge in a graph
    """

    def __init__(
        self,
        edge_id: str,
        start_node: Node,
        end_node: Node,
        edge_type: EdgeType = EdgeType.UNDIRECTED,
        data={},
    ):
        "simple edge constructor"
        super().__init__(oid=edge_id, odata=data)
        self.etype = edge_type
        self.start_node = start_node
        self.end_node = end_node

    def __eq__(self, n):
        if isinstance(n, Edge):
            return self.id() == n.id()
        return False

    def __str__(self):
        ""
        return (
            self.id()
            + "--"
            + str(self.type())
            + "--"
            + "::".join([str(k) + "-" + str(v) for k, v in self.data().items()])
            + "--"
            + str(self.start_node)
            + "--"
            + str(self.end_node)
        )

    def __hash__(self):
        return hash(self.__str__())

    def start(self) -> Node:
        return self.start_node

    def end(self) -> Node:
        return self.end_node

    def type(self) -> EdgeType:
        return self.etype

    def node_ids(self) -> Set[str]:
        ""
        ids = set()
        ids.add(self.start().id())
        ids.add(self.end().id())
        return ids

    def is_endvertice(self, n: Node) -> bool:
        "check if node is an end vertex"
        ids = self.node_ids()
        return n.id() in ids


"""!

\page edgepage Edge documentation

\section desc_sect Description

Edge is a set of nodes with two members generally designated as E.
...
"""
