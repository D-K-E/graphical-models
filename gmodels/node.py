"""
Node in a graph
"""
from typing import Dict, Set, Tuple, Optional
from gmodels.abstractobj import AbstractNode, AbstractEdge, EdgeType
from gmodels.abstractobj import NodePosition
from gmodels.info import EdgeInfo
from gmodels.graphobj import GraphObject


class Node(GraphObject):
    "A simple node in a graph"

    def __init__(self, node_id: str, data={}):
        "constructor for a node"
        super().__init__(oid=node_id, odata=data)

    def __eq__(self, n):
        if isinstance(n, Node):
            return self.id() == n.id()
        return False

    def __str__(self):
        ""
        return self.id() + "--" + str(self.data()) + "--" + str(self.info())

    def __hash__(self):
        return hash(self.__str__())
