"""!
\file graph.py

\defgroup graphgroup Graph and Related Objects

Contains a general graph object. Most of the functionality is based on 
Diestel 2017.

"""
from typing import Set, Optional, Callable, List, Tuple, Union, Dict, FrozenSet
from gmodels.gtypes.graphobj import GraphObject
from gmodels.gtypes.finitegraph import FiniteGraph
from gmodels.gtypes.basegraph import BaseGraph
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.gtypes.node import Node
from uuid import uuid4
import math


class Graph(FiniteGraph):
    """!
    Simple finite graph
    \f$ G = (V, E) \f$ where \f$ V \f$ is the vertex set and \f$ E \f$ is the edge set.
    """

    def __init__(
        self, gid: str, data={}, nodes: Set[Node] = None, edges: Set[Edge] = None
    ):
        """!
        \brief Graph Constructor

        \param gid unique graph id. In most cases we generate a random id with
        uuid4

        \param data is any data associated with the graph.

        \param nodes a node/vertex set.
        \param edges an edge set.

        \throws ValueError If the graph is trivial, we raise a value error, as
        most algorithms don't work with trivial graphs.

        We construct the graph from given node and edge set. For quick look up
        we store them in hash tables. The gdata member also stores an edge list
        representation, in order to facilitate some of the basic look up
        functionality concerning neighbours of vertices.

        \code{.py}

        >>> a = Node("a", {})  # b
        >>> b = Node("b", {})  # c
        >>> f = Node("f", {})  # d
        >>> e = Node("e", {})  # e
        >>> ab = Edge(
        >>>    "ab", start_node=a, end_node=b, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> be = Edge(
        >>>    "be", start_node=b, end_node=e, edge_type=EdgeType.UNDIRECTED
        >>> )
        >>> graph = Graph(
        >>>     "graph",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>     nodes=set([a, b, e, f]),
        >>>     edges=set([ab, be]),
        >>> )

        \endcode
        """
        super().__init__(gid=gid, nodes=nodes, edges=edges, data=data)
        #
        self.mk_nodes(ns=nodes, es=edges)
        self.mk_gdata()
        self.props = self.visit_graph_dfs(
            edge_generator=self.edges_of, check_cycle=True
        )

    @classmethod
    def from_base_graph(cls, bgraph: BaseGraph):
        ""
        fgraph = FiniteGraph.from_base_graph(bgraph)
        return cls.from_finite_graph(fgraph)

    @classmethod
    def from_finite_graph(cls, fgraph: FiniteGraph):
        ""
        nodes = fgraph.nodes()
        edges = fgraph.edges()
        data = fgraph.data()
        gid = fgraph.id()
        return Graph(gid=gid, nodes=nodes, edges=edges, data=data)

    @classmethod
    def from_edgeset(cls, edges: Set[Edge]):
        g = FiniteGraph.from_edgeset(edges)
        return cls.from_finite_graph(g)

    @classmethod
    def from_edge_node_set(cls, edges: Set[Edge], nodes: Set[Node]):
        g = FiniteGraph.from_edge_node_set(edges=edges, nodes=nodes)
        return cls.from_finite_graph(g)

    def mk_nodes(self, ns: Optional[Set[Node]], es: Optional[Set[Edge]]):
        """!
        \brief Obtain all nodes in a single set.

        \param ns set of nodes
        \param es set of edges

        We assume that node set and edge set might contain different nodes,
        that is \f$ V[G] = V[ns] \cup V[es] \f$
        We combine nodes given in both sets to create a final set of nodes
        for the graph
        """
        nodes = set()
        if ns is None:
            return
        for n in ns:
            nodes.add(n)
        if es is not None:
            for e in es:
                estart = e.start()
                eend = e.end()
                nodes.add(estart)
                nodes.add(eend)
        #
        self._nodes = {n.id(): n for n in nodes}

    def to_adjmat(self, vtype=int) -> Dict[Tuple[str, str], int]:
        """!
        \brief Transform adjacency list to adjacency matrix representation

        \param vtype the cast type for the entry of adjacency matrix.

        \return adjacency matrix whose keys are identifiers of nodes and values
        are flags whether there is an edge between them.

        \code{.py}

        >>> a = Node("a", {})  # b
        >>> b = Node("b", {})  # c
        >>> f = Node("f", {})  # d
        >>> e = Node("e", {})  # e
        >>> ae = Edge(
        >>>    "ae", start_node=a, end_node=e, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> af = Edge(
        >>>     "af", start_node=a, end_node=f, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> ef = Edge(
        >>>     "ef", start_node=e, end_node=f, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> ugraph1 = Graph(
        >>>     "graph",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>   nodes=set([a, b, e, f]),
        >>>   edges=set([ae, af, ef]),
        >>> )
        >>> mat = ugraph1.to_adjmat(vtype=bool)
        >>> mat == {
        >>>     ("b", "b"): False,
        >>>     ("b", "e"): False,
        >>>     ("b", "f"): False,
        >>>     ("b", "a"): False,
        >>>     ("e", "b"): False,
        >>>     ("e", "e"): False,
        >>>     ("e", "f"): True,
        >>>     ("e", "a"): True,
        >>>     ("f", "b"): False,
        >>>     ("f", "e"): True,
        >>>     ("f", "f"): False,
        >>>     ("f", "a"): True,
        >>>     ("a", "b"): False,
        >>>     ("a", "e"): True,
        >>>     ("a", "f"): True,
        >>>     ("a", "a"): False
        >>> }
        >>> True

        \endcode
        """
        gmat = {}
        for v in self.V:
            for k in self.V:
                common = set(self.gdata[v]).intersection(set(self.gdata[k]))
                gmat[(v, k)] = vtype(0)
        for edge in self.edges():
            tpl1 = (edge.start().id(), edge.end().id())
            tpl2 = (edge.end().id(), edge.start().id())
            if tpl1 in gmat:
                gmat[tpl1] = vtype(1)
            if edge.type() == EdgeType.UNDIRECTED:
                if tpl2 in gmat:
                    gmat[tpl2] = vtype(1)
        return gmat

    def transitive_closure_matrix(self) -> Dict[Tuple[str, str], bool]:
        """!
        \brief Obtain transitive closure matrix of a given graph

        Transitive closure is defined by Joyner, et. al. as:

        - Consider a digraph \f$G = (V, E)\f$ of order \f$n = |V |\f$. The
          transitive closure of G is defined as the digraph \f$G^{∗} = (V,
          E^{∗}) \f$ having the same vertex set as G. However, the edge set
          \f$E^{∗}\f$ of \f$G^{∗}\f$ consists of all edges uv such that there
          is a u-v path in G and \f$uv \not \in E\f$. The transitive closure
          \f$G^{*}\f$ answers an important question about G: If u and v are two
          distinct vertices of G, are they connected by a path with length ≥ 1?

        Variant of the Floyd-Roy-Warshall algorithm taken from Joyner,
        Phillips, Nguyen, Algorithmic Graph Theory, 2013, p.134

        \throws ValueError we raise a value error if the graph has a self loop.

        \code{.py}

        >>> a = Node("a", {})  # b
        >>> b = Node("b", {})  # c
        >>> f = Node("f", {})  # d
        >>> e = Node("e", {})  # e
        >>> ae = Edge(
        >>>    "ae", start_node=a, end_node=e, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> af = Edge(
        >>>     "af", start_node=a, end_node=f, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> ef = Edge(
        >>>     "ef", start_node=e, end_node=f, edge_type=EdgeType.UNDIRECTED
        >>> )

        >>> ugraph1 = Graph(
        >>>     "graph",
        >>>     data={"my": "graph", "data": "is", "very": "awesome"},
        >>>   nodes=set([a, b, e, f]),
        >>>   edges=set([ae, af, ef]),
        >>> )
        >>> mat == {
        >>>     ("a", "b"): True,
        >>>     ("a", "e"): True,
        >>>     ("a", "f"): True,
        >>>     ("b", "a"): False,
        >>>     ("b", "e"): False,
        >>>     ("b", "f"): False,
        >>>     ("e", "a"): True,
        >>>     ("e", "b"): True,
        >>>     ("e", "f"): True,
        >>>     ("f", "a"): True,
        >>>     ("f", "b"): True,
        >>>     ("f", "e"): True
        >>>   }
        >>> True

        \endcode
        """
        if self.has_self_loop():
            raise ValueError("Graph has a self loop")
        #
        n = len(self.gdata)
        T = self.to_adjmat(vtype=bool)
        for k in self.V.copy():
            for i in self.V.copy():
                for j in self.V.copy():
                    t_ij = T[(i, j)]
                    t_ik = T[(i, k)]
                    t_ki = T[(i, k)]
                    T[(i, j)] = t_ij or (t_ik and t_ki)
        T = {(k, i): v for (k, i), v in T.items() if k != i}
        return T

    def mk_gdata(self):
        """!
        \brief Create edge list representation of graph

        For each node we register the edges.
        """
        if self._nodes is not None:
            for vertex in self._nodes.values():
                self.gdata[vertex.id()] = []
            #
            for edge in self._edges.values():
                for node_id in edge.node_ids():
                    elist = self.gdata.get(node_id, None)
                    if elist is None:
                        self.gdata[node_id] = []
                    else:
                        self.gdata[node_id].append(edge.id())

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
        if isinstance(n, Graph):
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
            + "::".join([str(k) + "-" + str(v) for k, v in self.data().items()])
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

    def is_connected(self) -> bool:
        """!
        \brief Check if graph is connected
        If a graph has a single component, then we assume that it is connected
        graph

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
        >>> graph_2.is_connected()
        >>> True

        \endcode
        """
        return self.nb_components() == 1

    def is_homomorphism(
        self,
        phi_map: Callable[[Node], Node] = lambda x: x,
        psi_map: Callable[[Edge], Edge] = lambda x: x,
    ) -> bool:
        """!
        \brief Check if a function is a homomorphism on the given graph.

        \warning Absolutely untested function that tries to follow the definition
        given in Diestel 2017, p. 3. Basically if a function transforms 
        vertex set of graph but conserve adjacency properties of the graph,
        it is a homomorphism.
        
        """
        edges = self.edges()
        adjacency_of_vertices = set()
        nedges = set()
        nnodes = set()
        for e in edges:
            estart = e.start()
            eend = e.end()
            adjacency_of_vertices.add((estart, eend))
            nnodes.add(phi_map(estart))
            nnodes.add(phi_map(eend))
            nedges.add(psi_map(e))

        g = Graph.from_edge_node_set(edges=nedges, nodes=nnodes)
        for e in g.edges():
            estart = e.start()
            eend = e.end()
            if (estart, eend) not in adjacency_of_vertices:
                return False
        return True

    def graph_intersection(self, gs):
        """!
        """
        fgraph = super().graph_intersection(gs)
        return self.from_finite_graph(fgraph)

    def graph_difference(self, gs):
        """!
        """
        fgraph = super().graph_difference(gs)
        return self.from_finite_graph(fgraph)

    def graph_union(self, gs):
        """!
        """
        fgraph = super().graph_union(gs)
        return self.from_finite_graph(fgraph)

    def graph_symmetric_difference(self, gs):
        """!
        \brief symmetric set difference operation adapted for graph.
        """
        fgraph = super().graph_symmetric_difference(gs)
        return self.from_finite_graph(fgraph)

    def subtract_node(self, n: Node):
        ""
        fgraph = super().subtract_node(n)
        return self.from_finite_graph(fgraph)

    def subtract_edge(self, e: Edge) -> BaseGraph:

        fgraph = super().subtract_edge(e)
        return self.from_finite_graph(fgraph)

    def subtract_edge_with_nodes(self, e) -> BaseGraph:
        ""
        fgraph = super().subtract_edge_with_nodes(e)
        return self.from_finite_graph(fgraph)

    def add_edge(self, e: Edge):
        ""
        fgraph = super().add_edge(e)
        return self.from_finite_graph(fgraph)

    def visit_graph_dfs(
        self, edge_generator: Callable[[Node], Set[Node]], check_cycle: bool = False,
    ):
        """!
        \brief interior visit function for depth first enumeration of graph
        instance.

        \see dfs_forest() method for more information on parameters.
        """
        time = 0
        marked: Dict[str, bool] = {n: False for n in self.V}
        preds: Dict[str, Dict[str, str]] = {}
        Ts: Dict[str, Set[str]] = {}
        d: Dict[str, int] = {n: math.inf for n in self.V}
        f: Dict[str, int] = {n: math.inf for n in self.V}
        cycles: Dict[str, List[Dict[str, Union[str, int]]]] = {n: [] for n in self.V}
        component_counter = 0
        #
        for u in self.V:
            if marked[u] is False:
                pred: Dict[str, Optional[str]] = {n: None for n in self.V}
                T: Set[str] = set()
                self.dfs_forest(
                    u=u,
                    pred=pred,
                    cycles=cycles,
                    marked=marked,
                    d=d,
                    T=T,
                    f=f,
                    time=time,
                    check_cycle=check_cycle,
                    edge_generator=edge_generator,
                )
                component_counter += 1
                for child, parent in pred.copy().items():
                    if child != u and child is None:
                        pred.pop(child)
                Ts[u] = T
                preds[u] = pred
        #
        res = {
            "dfs-forest": self.from_preds_to_edgeset(preds),
            "first-visit-times": d,
            "last-visit-times": f,
            "components": Ts,
            "cycle-info": cycles,
            "nb-component": component_counter,
        }
        return res

    def from_preds_to_edgeset(
        self, preds: Dict[str, Dict[str, str]]
    ) -> Dict[str, Set[Edge]]:
        """!
        \brief obtain the edge set implied by the predecessor array.
        """
        esets: Dict[str, Set[Edge]] = {}
        for u, forest in preds.copy().items():
            eset: Set[Edge] = set()
            for child, parent in forest.items():
                cnode = self.V[child]
                if parent is not None:
                    pnode = self.V[parent]
                    eset = eset.union(self.edge_by_vertices(start=pnode, end=cnode))
            esets[u] = eset
        return esets

    def dfs_forest(
        self,
        u: str,
        pred: Dict[str, str],
        marked: Dict[str, int],
        d: Dict[str, int],
        f: Dict[str, int],
        T: Set[str],
        cycles: Dict[str, List[Dict[str, Union[str, int]]]],
        time: int,
        edge_generator: Callable[[Node], Set[Edge]],
        check_cycle: bool = False,
    ) -> Optional[Tuple[str, str]]:
        """!
        adapted for cycle detection
        dfs recursive forest from Erciyes 2018, Guide Graph ..., p.152 alg. 6.7

        \param f storing last visit times per node
        \param d storing first visit times per node
        \param cycles storing cycle info
        \param marked storing if node is visited
        \param pred storing the parent of nodes
        \param g graph we are searching for
        \param u node id
        \param T set of pred nodes
        \param time global visit counter
        \param check_cycle fill cycles if it is detected
        \param edge_generator generate edges of a vertex with respect to graph type
        """
        marked[u] = True
        time += 1
        d[u] = time
        unode = self.V[u]
        for edge in edge_generator(unode):
            vnode = edge.get_other(unode)
            v = vnode.id()
            if marked[v] is False:
                pred[v] = u
                T.add(v)
                self.dfs_forest(
                    u=v,
                    pred=pred,
                    marked=marked,
                    d=d,
                    f=f,
                    T=T,
                    cycles=cycles,
                    time=time,
                    check_cycle=check_cycle,
                    edge_generator=edge_generator,
                )
        #
        time += 1
        f[u] = time
        if check_cycle:
            # v ancestor, u visiting node
            # edge between them is a back edge
            # see p. 151, and p. 159-160
            unode = self.V[u]
            for edge in edge_generator(unode):
                vnode = edge.get_other(unode)
                vid = vnode.id()
                if pred[u] != vid:
                    first_visit = d.get(vid)
                    last_visit = f.get(vid)
                    cond = d[vid] < f[u]
                    if cond:
                        cycle_info = {
                            "ancestor": vid,
                            "before": u,
                            "ancestor-first-time-visit": d[vid],
                            "current-final-time-visit": f[u],
                        }
                        cycles[u].append(cycle_info)
        #
        return None

    def has_cycles(self) -> bool:
        """!
        \brief Check if graph instance contains cycles.
        This interpretation is from Diestel 2017, p. 8. The
        proof is provided in the given page.
        """
        md = self.min_degree()
        if md >= 2:
            return True
        return False

    def shortest_path_length(self) -> int:
        """!
        \brief Give the shortest possible path length for graph instance
        
        This interpretation is taken from Diestel 2017, p. 8. The proof
        is also given in the corresponding page.
        """
        return self.min_degree()

    def shortest_cycle_length(self) -> int:
        """!
        \brief Give the shortest possible cycle length for graph instance
        The interpretation comes from Diestel 2017, p. 8.
        """
        if self.has_cycles():
            return self.min_degree() + 1
        else:
            return 0

    def nb_components(self) -> int:
        """!
        \brief the number of connected components in the given graph.

        This number makes more sense in the case of undirected graphs as our
        algorithm is adapted for that case. It is computed as we are traversing
        the graph in dfs_forest()
        """
        return self.props["nb-component"]

    def is_tree(self) -> bool:
        """!
        \brief check if graph instance is a tree.

        This interpretation comes from Diestel 2017, p. 14 - 15.
        """
        nb_c = self.nb_components()
        nb_vs = len(self.nodes())
        nb_es = len(self.edges())
        return nb_c == 1 and nb_vs - 1 == nb_es

    def get_component_nodes(self, root_node_id: str) -> Set[Node]:
        """!
        \brief Get component nodes of a graph

        Given a root node id for a component, obtain its node set.
        """
        v = self.V[root_node_id]
        Ts = self.props["components"]
        T = Ts[root_node_id]
        T.add(v.id())
        return set([self.V[v] for v in T])

    def get_component(self, root_node_id: str) -> GraphObject:
        """!
        \brief get a component graph from graph instance

        As subgraphs are also graphs, components are in the strict sense a
        graph.
        """
        vertices = self.get_component_nodes(root_node_id)
        edges = [self.gdata[v.id()] for v in vertices]
        es: Set[Edge] = set()
        for elst in edges:
            for e in elst:
                es.add(self.E[e])

        return Graph(gid=str(uuid4()), nodes=vertices, edges=es)

    def get_components(self):
        """!
        \brief Get components of graph

        Each component is provided as a graph
        """
        if self.nb_components() == 1:
            return set([self])

        # Extract component roots
        component_roots = [k for k in self.props["dfs-forest"].keys()]
        return set([self.get_component(root_node_id=root) for root in component_roots])

    def get_components_as_node_sets(self) -> Set[FrozenSet[Node]]:
        """!
        \brief obtain component as a set of node sets.

        The node set members of the returning set are of type frozenset due to
        set being an unhashable type in python.
        """
        if self.nb_components() == 1:
            return set([frozenset(self.nodes())])

        # Extract component roots
        component_roots = [k for k in self.props["dfs-forest"].keys()]
        return set([frozenset(self.get_component_nodes(k)) for k in component_roots])

    def find_shortest_paths(
        self, n1: Node, edge_generator: Callable[[Node], Set[Edge]]
    ) -> Dict[str, Union[dict, set]]:
        """!
        \brief find shortest path from given node to all other nodes

        Applies the Breadth first search algorithm from Even and Guy Even 2012, p. 12

        \throws ValueError if given node is not found in graph instance
        """
        if not self.is_in(n1):
            raise ValueError("argument node is not in graph")
        nid = n1.id()
        Q = [nid]
        l_vs = {v: math.inf for v in self.V}
        l_vs[nid] = 0
        T = set([nid])
        P: Dict[str, Dict[str, str]] = {}
        P[nid] = {}
        while Q:
            u = Q.pop(0)
            unode = self.V[u]
            for edge in edge_generator(unode):
                vnode = edge.get_other(unode)
                vid = vnode.id()
                if vid not in T:
                    T.add(vid)
                    l_vs[vid] = int(l_vs[u] + 1)
                    P[nid][u] = vid
                    Q.append(vid)
        #
        T = set([self.V[t] for t in T])
        path_props = {"bfs-tree": P, "path-set": T, "top-sort": l_vs}
        return path_props

    def find_articulation_points(
        self, graph_maker: Callable[[Node], GraphObject]
    ) -> Set[Node]:
        """!
        \brief find articulation points of graph.

        Find the articulation points of a graph. An articulation point, also
        called cut vertex is defined as the vertex that separates two other
        vertices of the same component.

        The algorithm we implement here is the naive version see, Erciyes 2018,
        p. 228. For the definition of the cut vertex, see Diestel 2017, p. 11
        """
        nb_component = self.nb_components()
        points: Set[Node] = set()
        for node in self.nodes():
            graph = graph_maker(node)
            if graph.nb_components() > nb_component:
                points.add(node)
        return points

    def find_bridges(self, graph_maker: Callable[[Edge], GraphObject]) -> Set[Edge]:
        """!
        \brief find bridges of a given graph.

        A bridge is defined as the edge that separates its ends in the same
        component.
        The algorithm we implement here is the naive version provided by Erciyes 2018,
        p. 228. For the definition of the bridge, see Diestel 2017, p. 11
        """
        nb_component = self.nb_components()
        bridges: Set[Edge] = set()
        for edge in self.edges():
            graph = self.subtract(edge)
            if graph.nb_components() > nb_component:
                bridges.add(edge)
        return bridges

    def get_subgraph_by_vertices(
        self,
        vs: Set[Node],
        edge_policy: Callable[[Edge, Set[Node]], bool] = lambda x, ys: set(
            [x.start(), x.end()]
        ).issubset(ys)
        is True,
    ) -> GraphObject:
        """!
        Get the subgraph using vertices.

        \param vs set of vertices for the subgraph
        \param edge_policy determines which edges should be conserved. By
        default we conserve edges whose incident nodes are a subset of vs
        """
        es: Set[Edge] = set()
        for e in self.edges():
            if edge_policy(e, vs) is True:
                es.add(e)
        return Graph.from_edge_node_set(edges=es, nodes=vs)

    def __add__(
        self, a: Union[Set[Edge], Set[Node], Node, Edge, GraphObject]
    ) -> GraphObject:
        """!
        \brief overloads + sign for doing algebraic operations with graph
        objects.
        """
        if isinstance(a, Node):
            nodes = self.union(set([a]))
            return Graph(gid=str(uuid4()), data={}, nodes=nodes, edges=self.edges())
        elif isinstance(a, Edge):
            es = self.union(set([a]))
            return Graph(gid=str(uuid4()), data={}, nodes=self.nodes(), edges=es)
        else:
            return self.union(a)

    def __sub__(
        self, a: Union[Set[Edge], Set[Node], Node, Edge, GraphObject]
    ) -> GraphObject:
        """!
        \brief overloads - sign for doing algebraic operations with graph
        objects.
        """
        if isinstance(a, Node):
            nodes = self.difference(set([a]))
            return Graph(gid=str(uuid4()), data={}, nodes=nodes, edges=self.edges())
        elif isinstance(a, Edge):
            es = self.difference(set([a]))
            return Graph(gid=str(uuid4()), data={}, nodes=self.nodes(), edges=es)
        else:
            return self.difference(a)
