"""!
\file basegraph.py Absolute basic graph which implements the most basic
functionality for doing graph theoretical operations
"""
from typing import Callable, Dict, FrozenSet, List, Optional, Set, Union
from uuid import uuid4

from pygmodels.graphf.bgraphops import BaseGraphOps
from pygmodels.graphf.graphanalyzer import BaseGraphAnalyzer
from pygmodels.gtype.abstractobj import (
    AbstractEdge,
    AbstractGraph,
    AbstractNode,
)
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.gtype.graphobj import GraphObject
from pygmodels.gtype.node import Node


class BaseGraph(GraphObject, AbstractGraph):
    """!
    \brief Basic graph which implements the AbstractGraph interface
    """

    def __init__(
        self,
        gid: str,
        data={},
        nodes: Set[Node] = None,
        edges: Set[Edge] = None,
    ):
        super().__init__(oid=gid, odata=data)
        self._nodes: Optional[Dict[str, Node]] = None
        if nodes is not None:
            self._nodes = BaseGraphOps.get_nodes(ns=nodes, es=edges)
        self._edges: Optional[Dict[str, Edge]] = None
        if edges is not None:
            self._edges = {e.id(): e for e in edges}
        #
        self.gdata: Dict[str, List[str]] = BaseGraphOps.to_edgelist(self)
        if self._nodes is not None:
            self.is_empty = len(self._nodes) == 0
        else:
            self.is_empty = True

        is_trivial = BaseGraphAnalyzer.is_trivial(self)
        if is_trivial:
            msg = "This library is not compatible with computations with trivial graph"
            msg += "\nNodes: "
            msg += str(self._nodes.keys())
            msg += "\nEdges: " + str(self._edges.keys())
            raise ValueError(msg)

    @classmethod
    def from_abstract_graph(cls, g_: AbstractGraph):
        "Obtain base graph from AbstractGraph implementing object"
        if issubclass(g_, AbstractGraph):
            raise TypeError("Argument must implement AbstractGraph interface")
        nodes = set(g_.V.values())
        edges = set(g_.E.values())
        data = g_.data()
        gid = g_.id()
        return BaseGraph(gid=gid, data=data, nodes=nodes, edges=edges)

    def __eq__(self, n):
        """!
        \brief Check for equality

        This is not a strict check for equality of graphs. We simply check
        for ids. There is nothing mathematical about it. Should not be
        used in the context of graph algebra.
        \code{.py}

        >>> a = Node("a", {})  # a
        >>> e = Node("e", {})  # e
        >>> b = Node("b", {})  # e
        >>> ae = Edge(
        >>>    "ae", start_node=a, end_node=e, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> g1 = Graph("graph",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>     nodes=set([a, e]),
        >>>     edges=set([ae])
        >>> )
        >>> g2 = Graph("other",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>     nodes=set([a, e]),
        >>>     edges=set([ae])
        >>> )
        >>> g3 = Graph("graph",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>     nodes=set([a, e, b]),
        >>>     edges=set([ae])
        >>> )

        >>> g1 == g2
        >>> False
        >>> g1 == g3
        >>> True

        \endcode
        """
        if isinstance(n, BaseGraph):
            return self.id() == n.id()
        return False

    def __str__(self) -> str:
        """!
        \brief Obtain string representation of the graph.
        """
        return (
            self.id()
            + "--"
            + "::".join([str(n) for n in self._nodes])
            + "--"
            + "!!".join([str(n) for n in self._edges])
            + "--"
            + "::".join(
                [str(k) + "-" + str(v) for k, v in self.data().items()]
            )
        )

    def __hash__(self):
        """!
        \brief Create a hash value for the graph.

        Since the identifiers of graphs are randomly generated in most cases,
        hashing them by their string representation should not create a
        problem, because the string representation contains the identifier
        of the graph.
        """
        return hash(self.__str__())

    @property
    def V(self) -> Dict[str, Node]:
        """!
        \brief Obtain vertices of the graph

        \throws ValueError if node set is empty for the graph

        \code{.py}
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        e1 = Edge("e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED)
        g = Graph("graph", nodes=set([n1, n2]), edges=set([e1]))
        g.V
        # {"n1": Node, "n2": Node}

        \endcode
        """
        if self._nodes is None:
            raise ValueError("Nodes are None for this graph")
        return self._nodes

    @property
    def E(self) -> Dict[str, Edge]:
        """!
        \brief obtain edges of the graph
        \throws ValueError if edge set is empty for the graph.

        \code{.py}
        n1 = Node("n1", {})
        n2 = Node("n2", {})
        e1 = Edge("e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED)
        g = BaseGraph("graph", nodes=set([n1, n2]), edges=set([e1]))
        g.E
        # {"e1": Edge}

        \endcode

        """
        if self._edges is None:
            raise ValueError("Edges are None for this graph")
        return self._edges

    def is_neighbour_of(self, n1: Node, n2: Node) -> bool:
        """!
        \brief check if two nodes are neighbours
        We define the condition of neighborhood as having a common edge, not
        being the same

        \code{.py}

        >>> n1 = Node("n1", {})
        >>> n2 = Node("n2", {})
        >>> n3 = Node("n3", {})
        >>> n4 = Node("n4", {})
        >>> e1 = Edge(
        >>>     "e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> e2 = Edge(
        >>>     "e2", start_node=n2, end_node=n3, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> e3 = Edge(
        >>>     "e3", start_node=n3, end_node=n4, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> graph_2 = Graph(
        >>>   "g2",
        >>>   data={"my": "graph", "data": "is", "very": "awesome"},
        >>>   nodes=set([n1, n2, n3, n4]),
        >>>   edges=set([e1, e2, e3]),
        >>> )
        >>> graph_2.is_neighbour_of(n2, n3)
        >>> True
        >>> graph_2.is_neighbour_of(n2, n2)
        >>> False

        \endcode
        """

        def cond(n_1: Node, n_2: Node, e: Edge) -> bool:
            """!
            \brief neighborhood condition
            """
            estart = e.start()
            eend = e.end()
            c1 = estart == n_1 and eend == n_2
            c2 = estart == n_2 and eend == n_1
            return c1 or c2

        gdata = BaseGraphOps.to_edgelist(self)

        n1_edge_ids = set(gdata[n1.id()])
        n2_edge_ids = set(gdata[n2.id()])
        edge_ids = n1_edge_ids.intersection(n2_edge_ids)
        # filter self loops
        edges = set([self.E[e] for e in edge_ids])
        return self.is_related_to(n1=n1, n2=n2, condition=cond, es=edges)

    @classmethod
    def from_edgeset(cls, edges: Set[Edge]):
        """!
        \brief We construct the graph from given edge set using a random id.

        See \see Graph for more information

        We obtain nodes from edges then pass them to graph constructor.

        \code{.py}

        n1 = Node("n1", {})
        n2 = Node("n2", {})
        n3 = Node("n3", {})
        n4 = Node("n4", {})
        e1 = Edge(
            "e1", start_node=n1, end_node=n2, edge_type=EdgeType.UNDIRECTED
        )
        e2 = Edge(
            "e2", start_node=n2, end_node=n3, edge_type=EdgeType.UNDIRECTED
        )
        e3 = Edge(
            "e3", start_node=n3, end_node=n4, edge_type=EdgeType.UNDIRECTED
        )
        e4 = Edge(
            "e4", start_node=n1, end_node=n4, edge_type=EdgeType.UNDIRECTED
        )

        eset = set([e1, e2, e3, e4])

        g = Graph.from_edgeset(eset)
        \endcode
        """
        nodes: Set[Node] = set()
        for e in edges:
            nodes.add(e.start())
            nodes.add(e.end())
        return BaseGraph(gid=str(uuid4()), nodes=nodes, edges=edges)

    @classmethod
    def from_edge_node_set(cls, edges: Set[Edge], nodes: Set[Node]):
        """!
        \brief We construct the graph from given node, and edge sets using a random id.
        \see Graph for more information

        \param edges set of edges
        \param nodes set of nodes

        We iterate over set of edges and add the nodes that are not inside the
        node set. We pass both parameters to Graph constructor afterwards.
        """
        nodes = set(nodes)
        for e in edges:
            nodes.add(e.start())
            nodes.add(e.end())
        return BaseGraph(gid=str(uuid4()), nodes=nodes, edges=edges)

    @classmethod
    def based_on_node_set(
        cls, edges: Set[AbstractEdge], nodes: Set[AbstractNode]
    ):
        """!"""
        eset: Set[AbstractEdge] = set(
            [e for e in edges if set([e.start(), e.end()]).issubset(nodes)]
        )
        return cls.from_edge_node_set(edges=eset, nodes=nodes)

    def is_related_to(
        self,
        n1: Node,
        n2: Node,
        condition: Callable[[Node, Node, Edge], bool],
        es: FrozenSet[Edge] = None,
    ):
        """!
        \brief Generic function for applying proximity conditions on a node pair

        \param n1 first node subject to proximity condition
        \param n2 second node subject to proximity condition
        \param condition proximity condition in the form of a callable.
        \param es edge set. We query the proximity condition in this set if it
        is specified

        We check whether a proximity condition is valid for given two nodes.
        """
        if es is None:
            es = frozenset(self.E.values())
        for e in es:
            if condition(n1, n2, e) is True:
                return True
        return False
