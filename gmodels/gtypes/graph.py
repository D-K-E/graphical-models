"""!
\defgroup graphgroup Graph and Related Objects

"""
from typing import Set, Optional, Callable, List, Tuple, Union, Dict
from gmodels.gtypes.graphobj import GraphObject
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.gtypes.node import Node
from uuid import uuid4
import math


class Graph(GraphObject):
    """!
    Simple finite graph
    G = (V, E)
    V - {v}
    """

    def __init__(
        self, gid: str, data={}, nodes: Set[Node] = None, edges: Set[Edge] = None
    ):
        ""
        super().__init__(oid=gid, odata=data)
        self._nodes: Optional[Dict[str, Node]] = None
        if nodes is not None:
            self._nodes = {n.id(): n for n in nodes}
        self._edges: Optional[Dict[str, Edge]] = None
        if edges is not None:
            self._edges = {e.id(): e for e in edges}
        #
        self.gdata: Dict[str, List[str]] = {}
        if self._nodes is not None:
            self.is_empty = len(self._nodes) == 0
        else:
            self.is_empty = True

        if self.is_trivial():
            msg = "This library is not compatible with computations with trivial graph"
            msg += "\nNodes: "
            msg += str(self._nodes.keys())
            msg += "\nEdges: " + str(self._edges.keys())
            raise ValueError(msg)
        #
        self.mk_nodes(ns=nodes, es=edges)
        self.mk_gdata()
        self.props = self.visit_graph_dfs(
            edge_generator=self.edges_of, check_cycle=True
        )

    @classmethod
    def from_edgeset(cls, edges: Set[Edge]):
        """!
        """
        nodes: Set[Node] = set()
        for e in edges:
            nodes.add(e.start())
            nodes.add(e.end())
        return Graph(gid=str(uuid4()), nodes=nodes, edges=edges)

    def mk_nodes(self, ns: Optional[Set[Node]], es: Optional[Set[Edge]]):
        ""
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

    def to_adjmat(self, vtype=int):
        """!
        transform adjacency list to adjacency matrix representation
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

    def has_self_loop(self) -> bool:
        ""
        for edge in self.edges():
            if edge.start() == edge.end():
                return True
        return False

    def transitive_closure_matrix(self) -> Dict[Tuple[str, str], bool]:
        """!
        From algorithmic graph theory Joyner, Phillips, Nguyen, 2013, p.134
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
        "make graph data"
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
        if isinstance(n, Graph):
            return self.id() == n.id()
        return False

    def __str__(self):
        ""
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
        return hash(self.__str__())

    @property
    def V(self) -> Dict[str, Node]:
        "vertices of graph"
        if self._nodes is None:
            raise ValueError("Nodes are None for this graph")
        return self._nodes

    @property
    def E(self) -> Dict[str, Edge]:
        "edges of graph"
        if self._edges is None:
            raise ValueError("Edges are None for this graph")
        return self._edges

    def is_connected(self) -> bool:
        ""
        return all([len(es) != 0 for es in self.gdata.values()])

    def is_adjacent_of(self, e1: Edge, e2: Edge) -> bool:
        ""
        n1_ids = e1.node_ids()
        n2_ids = e2.node_ids()
        return len(n1_ids.intersection(n2_ids)) > 0

    def is_node_incident(self, n: Node, e: Edge) -> bool:
        ""
        return e.is_endvertice(n)

    def is_related_to(
        self,
        n1: Node,
        n2: Node,
        condition: Callable[[Node, Node, Edge], bool],
        es: Set[Edge] = None,
    ):
        """!
        are nodes related by an edge with respect to given condition
        """
        if es is None:
            es = self.edges()
        for e in es:
            if condition(n1, n2, e) is True:
                return True
        return False

    def is_neighbour_of(self, n1: Node, n2: Node) -> bool:
        """!
        """

        def cond(n_1: Node, n_2: Node, e: Edge) -> bool:
            ""
            estart = e.start()
            eend = e.end()
            c1 = estart == n_1 and eend == n_2
            c2 = estart == n_2 and eend == n_1
            return c1 or c2

        n1_edge_ids = set(self.gdata[n1.id()])
        n2_edge_ids = set(self.gdata[n2.id()])
        edge_ids = n1_edge_ids.intersection(n2_edge_ids)
        # filter self loops
        edges = set([self.E[e] for e in edge_ids])
        return self.is_related_to(n1=n1, n2=n2, condition=cond, es=edges)

    def is_node_independant_of(self, n1: Node, n2: Node) -> bool:
        return not self.is_neighbour_of(n1, n2)

    def is_stable(self, ns: Set[Node]) -> bool:
        ""
        if not self.contains_vertices(ns):
            raise ValueError("node set is not contained in graph")
        node_list = list(ns)
        while node_list:
            n1 = node_list.pop()
            for n2 in node_list:
                if self.is_neighbour_of(n1=n1, n2=n2):
                    return False
        return True

    def neighbours_of(self, n1: Node) -> Set[Node]:
        ""
        if not self.is_in(n1):
            raise ValueError("node is not in graph")
        neighbours = set()
        for n2 in self.nodes():
            if self.is_neighbour_of(n1=n1, n2=n2) is True:
                neighbours.add(n2)
        return neighbours

    def nb_neighbours_of(self, n: Node) -> int:
        return len(self.neighbours_of(n))

    def edges_of(self, n: Node) -> Set[Edge]:
        ""
        edge_ids = self.gdata[n.id()]
        return set([self.E[eid] for eid in edge_ids])

    def outgoing_edges_of(self, n: Node) -> Set[Edge]:
        ""
        return set([e for e in self.edges() if e.start() == n])

    def incoming_edges_of(self, n: Node) -> Set[Edge]:
        ""
        return set([e for e in self.edges() if e.end() == n])

    def edges_by_end(self, n: Node) -> Set[Edge]:
        ""
        edge_ids = self.gdata[n.id()]
        return set([self.E[e] for e in edge_ids if self.E[e].is_end(n)])

    def vertices(self) -> Set[Node]:
        return set([n for n in self.V.values()])

    def nodes(self) -> Set[Node]:
        return self.vertices()

    def edges(self) -> Set[Edge]:
        return set([n for n in self.E.values()])

    def is_in(self, ne: Union[Node, Edge]) -> bool:
        ""
        if isinstance(ne, Node):
            return ne.id() in self.gdata
        else:
            check = False
            nid = ne.id()
            for elist in self.gdata.values():
                if nid in elist:
                    check = True
            return check

    def order(self) -> int:
        return len(self.V)

    def nb_edges(self) -> int:
        return len(self.E)

    def is_trivial(self) -> bool:
        "check if graph is trivial"
        return self.order() < 2

    def vertex_by_id(self, node_id: str) -> Node:
        if node_id not in self.V:
            raise ValueError("node id not in graph")
        return self.V[node_id]

    def edge_by_id(self, edge_id: str) -> Edge:
        ""
        if edge_id not in self.E:
            raise ValueError("edge id not in graph")
        return self.E[edge_id]

    def edge_by_vertices(self, n1: Node, n2: Node) -> Set[Edge]:
        """!
        """
        if not self.is_in(n1) or not self.is_in(n2):
            raise ValueError("one of the nodes is not present in graph")
        n1id = n1.id()
        n2id = n2.id()
        first_eset = set(self.gdata[n1id])
        second_eset = set(self.gdata[n2id])
        common_edge_ids = first_eset.intersection(second_eset)
        if len(common_edge_ids) == 0:
            raise ValueError("No common edges between given nodes")
        return set([self.E[e] for e in common_edge_ids])

    def vertices_of(self, e: Edge) -> Tuple[Node, Node]:
        ""
        if self.is_in(e):
            return (e.start(), e.end())
        else:
            raise ValueError("edge not in graph")

    def is_homomorphism(
        self,
        fn: Callable[[Node], Node],
        graph_builder: Callable[[Set[Node]], GraphObject],
    ) -> bool:
        "Check if a function is a homomorphism"
        edges = self.edges()
        nodes = set()
        for n in self.nodes():
            nodes.add(fn(n))
        ngraph = graph_builder(nodes)

        for e in edges:
            vs = self.vertices_of(e)
            v1 = vs[0]
            v2 = vs[1]
            v1_ = fn(v1)
            v2_ = fn(v2)
            nedge = ngraph.edge_by_vertices(v1_, v2_)
            if nedge is None:
                return False
        return True

    def set_op(
        self,
        obj: Union[Set[Node], Set[Edge], GraphObject],
        op: Callable[[Union[Set[Node], Set[Edge]]], Union[Set[Node], Set[Edge], bool]],
    ) -> Optional[Union[Set[Node], Set[Edge], bool]]:
        ""
        if isinstance(obj, set):
            lst = list(obj)
            if isinstance(lst[0], Node):
                return op(self.nodes())
            else:
                return op(self.edges())
        elif not isinstance(obj, Graph):
            raise TypeError("object should be either node/edge set or graph")
        return None

    def intersection(
        self, aset: Union[Set[Node], Set[Edge], GraphObject]
    ) -> Union[Set[Node], Set[Edge], GraphObject]:
        "intersection of either node or edge set"
        v = self.set_op(obj=aset, op=lambda x: x.intersection(aset))
        if v is None:
            return self.graph_intersection(aset)
        return v

    def union(
        self, aset: Union[Set[Node], Set[Edge], GraphObject]
    ) -> Union[Set[Node], Set[Edge], GraphObject]:
        ""
        v = self.set_op(obj=aset, op=lambda x: x.union(aset))
        if v is None:
            return self.graph_union(aset)
        return v

    def difference(
        self, aset: Union[Set[Node], Set[Edge], GraphObject]
    ) -> Union[Set[Node], Set[Edge], GraphObject]:
        ""
        v = self.set_op(obj=aset, op=lambda x: x.difference(aset))
        if v is None:
            return self.graph_difference(aset)
        return v

    def symmetric_difference(
        self, aset: Union[Set[Node], Set[Edge], GraphObject]
    ) -> Union[Set[Node], Set[Edge], GraphObject]:
        ""
        v = self.set_op(obj=aset, op=lambda x: x.symmetric_difference(aset))
        if v is None:
            return self.graph_symmetric_difference(aset)
        return v

    def contains(self, a: Union[Set[Edge], Set[Node], GraphObject]) -> bool:
        ""
        v = self.set_op(obj=a, op=lambda x: x.intersection(a) == a)
        if v is None:
            return self.contains(a.nodes()) and self.contains(a.edges())
        return v

    def graph_intersection(self, gs):
        ""
        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.intersection(es)
        ns_ = self.intersection(ns)
        return Graph(gid=str(uuid4()), nodes=ns_, edges=es_)

    def graph_union(self, gs):
        ""
        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.union(es)
        ns_ = self.union(ns)
        return Graph(gid=str(uuid4()), nodes=ns_, edges=es_)

    def graph_difference(self, gs):
        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.difference(es)
        # ensure that edges do not contain
        # a node that is in gs
        ess = set()
        for e in es_:
            ids = e.node_ids()
            if all([i not in gs.V for i in ids]):
                ess.add(e)
        ns_ = self.difference(ns)
        return Graph(gid=str(uuid4()), nodes=ns_, edges=ess)

    def graph_symmetric_difference(self, gs):
        ns: Set[Node] = gs.nodes()
        es: Set[Edge] = gs.edges()
        es_ = self.symmetric_difference(es)
        ns_ = self.symmetric_difference(ns)
        return Graph(gid=str(uuid4()), nodes=ns_, edges=es_)

    def _subtract_node(self, n: Node) -> Tuple[Set[Node], Set[Edge]]:
        "subtract a given node from graph"
        if not isinstance(n, Node):
            raise TypeError("argument is not an instance of node")
        nodes = self.nodes()
        edges = self.edges()
        nnodes: Set[Node] = set()
        nedges: Set[Edge] = set()
        n_id = n.id()
        for node in nodes:
            if node != n:
                nnodes.add(node)
        for edge in edges:
            node_ids = edge.node_ids()
            if n_id not in node_ids:
                nedges.add(edge)
        return (nnodes, nedges)

    def subtract_node_from_self(self, n: Node):
        ""
        nodes, edges = self._subtract_node(n)
        self._nodes = {n.id(): n for n in nodes}
        self._edges = {e.id(): e for e in edges}

    def subtract_node(self, n: Node):
        ""
        nodes, edges = self._subtract_node(n)
        data = self.data()
        return Graph(gid=str(uuid4()), data=data, nodes=nodes, edges=edges)

    def subtract_nodes_from_self(self, ns: Set[Node]):
        ""
        for n in ns:
            self.subtract_node_from_self(n)

    def subtract_nodes(self, ns: Set[Node]):
        ""
        for n in ns:
            self = self.subtract_node(n)

    def _subtract_edge(self, e: Edge) -> Set[Edge]:
        "subtract a given node from graph"
        if not isinstance(e, Edge):
            raise TypeError("argument is not an instance of edge")
        edges = self.edges()
        nedges: Set[Edge] = set()
        for edge in edges:
            if e != edge:
                nedges.add(edge)
        return nedges

    def subtract_edge_from_self(self, e: Edge):
        ""
        edges = self._subtract_edge(e)
        self._edges = {e.id(): e for e in edges}

    def subtract_edge(self, e: Edge) -> GraphObject:
        ""
        edges = self._subtract_edge(e)
        return Graph(
            gid=str(uuid4()), data=self.data(), nodes=self.nodes(), edges=edges
        )

    def subtract_edge_with_nodes(self, e) -> GraphObject:
        ""
        edges = self._subtract_edge(e)
        enode1, enode2 = e.start(), e.end()
        nodes = self.nodes()
        nodes = nodes.difference(set([enode1, enode2]))
        return Graph(gid=str(uuid4()), nodes=nodes, edges=edges)

    def subtract(self, a: Union[Node, Edge]):
        ""
        if isinstance(a, Node):
            return self.subtract_node(a)
        return self.subtract_edge(a)

    def subtract_edges_from_self(self, es: Set[Edge]):
        ""
        for e in es:
            self.subtract_edge_from_self(e)

    def subtract_edges(self, es: Set[Edge]):
        ""
        for e in es:
            self = self.subtract_edge(e)

    def added_edge_between_if_none(self, n1: Node, n2: Node) -> bool:
        """!
        Add edges between nodes if there are no edges in between
        """
        try:
            es = self.edge_by_vertices(n1, n2)
        except ValueError:
            e = Edge(edge_id=str(uuid4()), data={}, start_node=n1, end_node=n2)
            self.add_edge_to_self(e)
            return True
        return False

    def add_edge_to_self(self, e: Edge):
        ""
        edges = self.edges()
        edges.add(e)
        self._edges = {e.id(): e for e in edges}

    def add_edge(self, e: Edge):
        ""
        edges = self.edges()
        edges.add(e)
        return Graph(
            gid=str(uuid4()), data=self.data(), nodes=self.nodes(), edges=edges
        )

    def add_edges_to_self(self, es: Set[Edge]):
        ""
        for e in es:
            self.add_edges_to_self(e)

    def add_edges(self, es: Set[Edge]):
        ""
        for e in es:
            self = self.add_edge(e)

    def comp_degree(self, fn: Callable[[int, int], bool], comp_val: int) -> int:
        ""
        compare_v = comp_val
        for nid in self.V:
            nb_edges = len(self.gdata[nid])
            if fn(nb_edges, compare_v):
                compare_v = nb_edges
        return compare_v

    def max_degree(self) -> int:
        ""
        v = self.comp_degree(
            fn=lambda nb_edges, compare: nb_edges > compare, comp_val=0
        )
        return v

    def max_degree_vs(self) -> Set[Node]:
        ""
        md = self.max_degree()
        nodes = set()
        for nid in self.V:
            if len(self.gdata[nid]) == md:
                nodes.add(self.V[nid])
        return nodes

    def min_degree(self) -> int:
        ""
        return int(
            self.comp_degree(
                fn=lambda nb_edges, compare: nb_edges < compare, comp_val=math.inf
            )
        )

    def min_degree_vs(self) -> Set[Node]:
        ""
        md = self.min_degree()
        nodes = set()
        for nid in self.V:
            if len(self.gdata[nid]) == md:
                nodes.add(self.V[nid])
        return nodes

    def average_degree(self) -> float:
        """!
        \f d(G) = \frac{1}{V[G]} \sum_{v \in V[G]} d(v) \f
        """
        return sum([len(self.gdata[nid]) for nid in self.V]) / len(self.V)

    def edge_vertex_ratio(self) -> float:
        ""
        return len(self.E) / len(self.V)

    def ev_ratio_from_average_degree(self, average_degree: float):
        """!
        \f |E[G]| = \frac{1}{2} \sum_{v \in V[G]} d(v) = 1/2 * d(G) * |V[G]| \f
        """
        return average_degree / 2

    def ev_ratio(self):
        ""
        return self.ev_ratio_from_average_degree(self.average_degree())

    def visit_graph_dfs(
        self, edge_generator: Callable[[Node], Set[Node]], check_cycle: bool = False,
    ):
        ""
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
        ""
        esets: Dict[str, Set[Edge]] = {}
        for u, forest in preds.copy().items():
            eset: Set[Edge] = set()
            for child, parent in forest.items():
                cnode = self.V[child]
                if parent is not None:
                    pnode = self.V[parent]
                    eset = eset.union(self.edge_by_vertices(n1=pnode, n2=cnode))
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
        see Diestel 2017, p. 8
        """
        md = self.min_degree()
        if md >= 2:
            return True
        return False

    def shortest_path_length(self) -> int:
        """!
        see Diestel 2017, p. 8
        """
        return self.min_degree()

    def shortest_cycle_length(self) -> int:
        """!
        see Diestel 2017, p. 8
        """
        if self.has_cycles():
            return self.min_degree() + 1
        else:
            return 0

    def nb_components(self) -> int:
        return self.props["nb-component"]

    def is_tree(self) -> bool:
        """!
        see Diestel 2017, p. 14 - 15
        """
        nb_c = self.nb_components()
        nb_vs = len(self.nodes())
        nb_es = len(self.edges())
        return nb_c == 1 and nb_vs - 1 == nb_es

    def child_from_parent(
        self, current: str, preds: Dict[str, Optional[str]], root: str,
    ) -> Optional[str]:
        ""
        c, p = None, None
        for child, parent_id in preds.copy().items():
            if parent_id == current:
                preds.pop(child)
                c = child
        for child, parent_id in preds.copy().items():
            if child == current:
                p = preds.pop(child)
        if c is not None:
            return c
        if p is not None:
            return p
        return None

    def get_component(self, node_id: str) -> GraphObject:
        """!
        get a component from graph
        """
        v = self.V[node_id]
        Ts = self.props["components"]
        T = Ts[node_id]
        T.add(v.id())
        vertices = [self.V[v] for v in T]
        edges = [self.gdata[v] for v in T]
        es: Set[Edge] = set()
        for elst in edges:
            for e in elst:
                es.add(self.E[e])

        return Graph(gid=str(uuid4()), nodes=vertices, edges=es)

    def get_components(self):
        """!
        Get components of graph
        """
        if self.nb_components() == 1:
            return set([self])

        # Extract component roots
        component_roots = [k for k in self.props["dfs-forest"].keys()]
        return set([self.get_component(node_id=root) for root in component_roots])

    def find_shortest_paths(
        self, n1: Node, edge_generator: Callable[[Node], Set[Edge]]
    ) -> Dict[str, Union[dict, set]]:
        """!
        Breadth first search
        Even and Guy Even 2012, p. 12
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
        naive version see, Erciyes 2018, p. 228
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
        naive version
        """
        nb_component = self.nb_components()
        bridges: Set[Edge] = set()
        for edge in self.edges():
            graph = self.subtract(edge)
            if graph.nb_components() > nb_component:
                bridges.add(edge)
        return bridges

    def __add__(
        self, a: Union[Set[Edge], Set[Node], Node, Edge, GraphObject]
    ) -> GraphObject:
        ""
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
        ""
        if isinstance(a, Node):
            nodes = self.difference(set([a]))
            return Graph(gid=str(uuid4()), data={}, nodes=nodes, edges=self.edges())
        elif isinstance(a, Edge):
            es = self.difference(set([a]))
            return Graph(gid=str(uuid4()), data={}, nodes=self.nodes(), edges=es)
        else:
            return self.difference(a)
