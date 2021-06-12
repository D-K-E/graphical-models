"""!
\file digraph.py

# Directed Graph

This is basically a Graph with directed edges. This has implications on several
algorithms. Most notably connected components algorithm does not work the same
way. The minimum spanning tree also does not work. We need to differentiate the
positioning of nodes in edges as well. Sometimes it is also represented as \f[
G = (V, A) \f] where A is arcs.

Whenever possible we simply change the edge generation strategy in order to use
the parent's algorithm.

"""
from typing import Set, Callable
from gmodels.gtypes.edge import Edge
from gmodels.gtypes.node import Node
from gmodels.gtypes.abstractobj import EdgeType
from gmodels.gtypes.graph import Graph
from gmodels.gtypes.undigraph import UndiGraph
from gmodels.gops.gtraverser import GraphTraverser
from uuid import uuid4


class DiGraph(Graph):
    """!
    \brief Directed graph implementation
    """

    def __init__(
        self, gid: str, data={}, nodes: Set[Node] = None, edges: Set[Edge] = None
    ):
        """!
        \brief Constructor for DiGraph

        More or less what we have in Graph.
        We just make sure every edge is a directed edge.
        \sa Graph for parameters.

        \throws ValueError if there is any undirected edge among the argument
        edge set.
        """

        if edges is not None:
            for edge in edges:
                if edge.type() == EdgeType.UNDIRECTED:
                    raise ValueError(
                        "Can not instantiate directed graph with" + " undirected edges"
                    )
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)
        fgraph = self.to_finite_graph()
        self.path_props = {v.id(): self.find_shortest_paths(v) for v in self.nodes()}
        self.dprops = GraphTraverser.visit_graph_dfs(
            self.to_finite_graph(),
            edge_generator=self.outgoing_edges_of,
            check_cycle=True,
        )

    @classmethod
    def from_graph(cls, g: Graph):
        """!
        \brief make DiGraph from Graph

        \param g argument graph

        We give a random id for the resulting DiGraph.
        """
        return DiGraph(
            gid=str(uuid4()), data=g.data(), nodes=g.nodes(), edges=g.edges()
        )

    def is_family_of(self, src: Node, dst: Node) -> bool:
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
        for e in self.edges():
            # dst is child of src
            child_cond = e.start() == src and e.end() == dst
            # dst is parent of src
            parent_cond = e.start() == dst and e.end() == src
            if child_cond or parent_cond:
                return True
        return False

    def is_parent_of(self, parent: Node, child: Node) -> bool:
        """!
        \brief check if one node is parent of another node

        We define the notion of parent node as the following.
        For all e in E[G] and for all {v,w} in V[e] if e is an outgoing edge of
        v and incoming edge of w than v is parent of w.
        """

        def cond(n_1: Node, n_2: Node, e: Edge):
            ""
            c = n_1 == e.start() and e.end() == n_2
            return c

        return self.is_related_to(n1=parent, n2=child, condition=cond)

    def is_child_of(self, child: Node, parent: Node) -> bool:
        """!
        \brief  check if one node is child of another node

        We define the notion of child node as the following.
        For all e in E[G] and for all {v,w} in V[e] if e is an incoming edge of
        v and outgoing edge of w than v is child of w.
        As you can see from the definition provided in is_parent_of() as well,
        if v is child of w, then w is parent of v.
        """
        return self.is_parent_of(parent=parent, child=child)

    def edge_by_vertices(self, start: Node, end: Node) -> Set[Edge]:
        """!
        \brief obtain edge by using its start and end node.

        \throws ValueError If any of the arguments are not found in this graph we
        throw value error.
        """
        if not self.is_in(start) or not self.is_in(end):
            raise ValueError("argument nodes are not in graph")
        #
        eset: Set[Edge] = set()
        for e in self.edges():
            if e.start().id() == start.id() and e.end().id() == end.id():
                eset.add(e)
        return eset

    def is_adjacent_of(self, e1: Edge, e2: Edge) -> bool:
        """!
        \brief check if edges have a common node
        """
        n1_ids = e1.node_ids()
        n2_ids = e2.node_ids()
        return len(n1_ids.intersection(n2_ids)) > 0

    def family_set_of(
        self,
        n: Node,
        fcond: Callable[[Edge, Node], bool],
        enode_fn: Callable[[Edge], Node],
    ):
        """!
        \brief obtain direct family set of nodes from given argument

        \param n argument node whose family set, we are interested in
        \param fcond family condition function
        \param enode_fn node extracting function. Extracts node from given edge

        \throws ValueError if the argument does not belong to this graph we
        throw value error.
        """
        if not self.is_in(n):
            raise ValueError("node not in graph")
        family = set()
        for e in self.edges():
            if fcond(e, n) is True:
                family.add(enode_fn(e))
        return family

    def children_of(self, n: Node) -> Set[Node]:
        """!
        \brief obtain direct child set of nodes from given argument

        \throws ValueError if the argument does not belong to this graph we
        throw value error.
        """
        return self.family_set_of(
            n=n,
            fcond=lambda e, node: e.start().id() == node.id(),
            enode_fn=lambda e: e.end(),
        )

    def parents_of(self, n: Node) -> Set[Node]:
        """!
        \brief obtain direct parent set of nodes from given argument

        \throws ValueError if the argument does not belong to this graph we
        throw value error.
        """
        return self.family_set_of(
            n=n,
            fcond=lambda e, node: e.end().id() == node.id(),
            enode_fn=lambda e: e.start(),
        )

    def to_undirected(self) -> UndiGraph:
        """!
        to undirected graph
        """
        nodes = self.nodes()
        edges = self.edges()
        nedges = set()
        nnodes = set([n for n in nodes])
        for e in edges:
            e.set_type(etype=EdgeType.UNDIRECTED)
            nedges.add(e)
        return UndiGraph(gid=str(uuid4()), data=self.data(), nodes=nnodes, edges=nedges)

    def in_degree_of(self, n: Node) -> int:
        return len(self.parents_of(n))

    def out_degree_of(self, n: Node) -> int:
        return len(self.children_of(n))

    def find_shortest_paths(self, n: Node):
        """!
        """
        return GraphTraverser.find_shortest_paths(
            self, n1=n, edge_generator=self.outgoing_edges_of
        )

    def check_for_path(self, n1: Node, n2: Node) -> bool:
        "check if there is a path between nodes"
        path_props = self.path_props[n1.id()]
        pset = path_props["path-set"]
        return n2 in pset

    def find_transitive_closure(self) -> Graph:
        """!
        From algorithmic graph theory Joyner, Phillips, Nguyen, 2013, p.134
        """
        T = self.transitive_closure_matrix()
        nodes = set()
        edges = set()
        for tpl, tval in T.items():
            if tval is False:
                n1 = self.V[tpl[0]]
                n2 = self.V[tpl[1]]
                nodes.add(n1)
                nodes.add(n2)
                e = Edge(
                    edge_id=str(uuid4()),
                    start_node=n1,
                    end_node=n2,
                    edge_type=EdgeType.DIRECTED,
                )
                edges.add(e)

        return DiGraph(gid=str(uuid4()), nodes=nodes, edges=edges)
