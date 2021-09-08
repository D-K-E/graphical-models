"""!
Probabilistic Graphic Model - LWF Chain Graph

Partially Directed Acyclic Graph as in Koller, Friedman 2009, p. 37
"""
from typing import Dict, Set, Tuple, Union
from uuid import uuid4

from pygmodels.gmodel.graph import Graph
from pygmodels.gmodel.tree import Tree
from pygmodels.gmodel.undigraph import UndiGraph
from pygmodels.graphf.graphanalyzer import BaseGraphAnalyzer
from pygmodels.graphf.graphops import BaseGraphOps
from pygmodels.gtype.edge import Edge, EdgeType
from pygmodels.gtype.node import Node
from pygmodels.pgmodel.markov import ConditionalRandomField, MarkovNetwork
from pygmodels.pgmtype.factor import Factor
from pygmodels.pgmtype.pgmodel import PGModel
from pygmodels.pgmtype.randomvariable import NumCatRVariable


class LWFChainGraph(PGModel):
    """!
    LWF Chain graph model generalizing bayes networks and markov random fields
    """

    def __init__(
        self,
        gid: str,
        nodes: Set[NumCatRVariable],
        edges: Set[Edge],
        factors: Set[Factor],
        data={},
    ):
        """"""
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges, factors=factors)
        self.ccomponents = list(self.get_chain_components())
        self.chain_components: Dict[str, Set[UndiGraph]] = {
            str(uuid4()): c for c in self.ccomponents
        }
        self.nb_components = (
            len(self.ccomponents) if len(self.chain_components) != 0 else 1
        )
        self.dag_components = self.get_chain_dag()

    def moralize(self) -> MarkovNetwork:
        """!
        Moralize given chain graph: For any \f X,Y \in Pa_{K_i} \f add an edge
        between them if it does not exist. Then drop the direction of edges.
        """
        edges = set(self.E)
        enodes = set([frozenset([e.start(), e.end()]) for e in edges])
        # add edges
        for cid in range(len(self.ccomponents)):
            pa_k_i: Set[NumCatRVariable] = self.parents_of_K(i=cid)
            pa_k_i_cp = set([p for p in pa_k_i])
            while len(pa_k_i_cp) > 0:
                parent_node = pa_k_i_cp.pop()
                for pnode in pa_k_i:
                    is_n_ind = BaseGraphAnalyzer.is_node_independent_of(
                        self, parent_node, pnode
                    )
                    if (
                        is_n_ind is True
                        and frozenset([parent_node, pnode]).issubset(enodes) is False
                    ):
                        e = Edge(
                            edge_id=str(uuid4()),
                            start_node=parent_node,
                            end_node=pnode,
                            edge_type=EdgeType.UNDIRECTED,
                        )
                        edges.add(e)

        # drop orientation
        nedges = set()
        for e in edges:
            if e.type() == EdgeType.DIRECTED:
                ne = Edge(
                    edge_id=str(uuid4()),
                    start_node=e.start(),
                    end_node=e.end(),
                    edge_type=EdgeType.UNDIRECTED,
                    data=e.data(),
                )
                nedges.add(ne)
            else:
                nedges.add(e)
        #
        return MarkovNetwork(
            gid=str(uuid4()),
            nodes=self.V,
            edges=nedges,
            factors=self.factors(),
        )

    def component_to_crf(self, i: int) -> ConditionalRandomField:
        """!
        get conditional random field corresponding to chain component
        with respect to Koller, Friedman 2009, p. 148-149
        """
        component = self.K_nodes(i)
        parents = self.parents_of_K(i)
        fs = set()
        for f in self.factors():
            if f.scope_vars().issubset(parents.union(component)) is True:
                fs.add(f)
        return ConditionalRandomField(
            gid=str(uuid4()), observed_vars=parents, target_vars=component, factors=fs,
        )

    def to_crfs(self) -> Set[ConditionalRandomField]:
        """"""
        return set([self.component_to_crf(i) for i in range(len(self.ccomponents))])

    def chain_component(self, dag_id: str) -> Set[UndiGraph]:
        """!"""
        return self.chain_components[dag_id]

    def K(self, i: int) -> Union[NumCatRVariable, UndiGraph]:
        """!
        From Koller, Friedman 2009, p. 148
        """
        return self.ccomponents[i]

    def K_nodes(self, i: int) -> Set[NumCatRVariable]:
        """!"""
        K = self.K(i)
        if isinstance(K, UndiGraph):
            return K.nodes()
        elif isinstance(K, frozenset):
            return set(K)
        else:
            raise TypeError("Unknown component type")

    def parents_of_K(self, i: int) -> Set[NumCatRVariable]:
        """!
        obtain parent nodes of vertices of chain component K.
        Models V[Pa(K_i)]
        """
        K_i: Union[UndiGraph, Set[NumCatRVariable]] = self.K(i)
        Pa_Ki_nodes = set()
        if isinstance(K_i, UndiGraph):
            knodes = K_i.V
            for kn in knodes:
                for pa_k in self.parents_of(kn):
                    if pa_k not in knodes:
                        Pa_Ki_nodes.add(pa_k)
        elif isinstance(K_i, frozenset) is True:
            for k_i in K_i:
                for pa_k in self.parents_of(k_i):
                    Pa_Ki_nodes.add(pa_k)
        else:
            raise TypeError("Component has an unacceptable type:" + str(type(K_i)))
        return Pa_Ki_nodes

    def parents_of(self, n: NumCatRVariable) -> Set[NumCatRVariable]:
        """"""
        return set(
            [
                n_p
                for n_p in self.V
                if self.is_parent_of(parent=n_p, child=n) is True
            ]
        )

    def get_chain_components(self) -> Set[Union[UndiGraph, NumCatRVariable]]:
        """!
        Based on the equivalence relation defined by Drton 2009
        and the answer in so: https://stackoverflow.com/a/14518552/7330813

        The equivalence relation: Define two vertices \fv_0\f and \fv_k\f in a
        chain graph G to be equivalent if there exists a path \f(v_0,...,
        v_k)\f such that \fv_i − v_{i+1}\f in G for all 0 ≤ i ≤ k − 1. The
        equivalence classes under this equivalence relation are the chain
        components of G.
        Basically the connected components of an undirected graph whose
        vertices are incident with undirected edges of the given chain graph,
        and nodes that are only pointed by directed edges.
        """
        edges = set()
        for e in self.E:
            if e.type() == EdgeType.UNDIRECTED:
                edges.add(e)

        undi = UndiGraph.from_graph(
            Graph.from_edge_node_set(edges=edges, nodes=self.V)
        )
        chain_components: Set[Union[Set[Node], UndiGraph]] = set()
        for cg in undi.get_components_as_node_sets():
            if len(cg) > 1:
                component = UndiGraph.from_graph(undi.get_subgraph_by_vertices(vs=cg))
                chain_components.add(component)
            else:
                chain_components.add(cg)

        return chain_components

    def get_chain_component_factors(self) -> Dict[str, Set[Factor]]:
        """"""
        component_factors = {}
        fs = self.factors()
        for gd, component in self.chain_components.items():
            component_factors[gd] = set()
            cnodes = component.nodes()
            for f in fs:
                if self.scope_of(f).issubset(cnodes) is True:
                    component_factors[gd].add(f)
        return component_factors

    def check_edge_between_components(self, e: Edge) -> Tuple[bool, str, str]:
        """!
        Check if the given edge is between chain components
        """
        estart = e.start()
        eend = e.end()
        start_component_id = None
        end_component_id = None
        for cid, component in self.chain_components.items():
            if isinstance(component, UndiGraph) is True:
                cnodes = component.V
                if estart in cnodes:
                    start_component_id = cid
                if eend in cnodes:
                    end_component_id = cid
            else:
                if estart in component:
                    start_component_id = cid
                if eend in component:
                    end_component_id = cid
        return (
            start_component_id != end_component_id,
            start_component_id,
            end_component_id,
        )

    def get_chain_dag(self):
        """!
        Get the directed acyclic graph composed of chain components
        """
        dag_nodes = {
            cid: NumCatRVariable(
                node_id=cid,
                input_data={"outcome-values": [True, False]},
                marginal_distribution=lambda x: 1.0 / self.nb_components,
            )
            for cid in self.chain_components
        }
        dag_edges = set()
        for e in self.E:
            if e.type() == EdgeType.DIRECTED:
                (
                    edge_between_components_check,
                    start_component_id,
                    end_component_id,
                ) = self.check_edge_between_components(e)
                if edge_between_components_check is True and (
                    start_component_id is not None and end_component_id is not None
                ):
                    dag_edge = Edge(
                        edge_id=str(uuid4()),
                        start_node=dag_nodes[start_component_id],
                        end_node=dag_nodes[end_component_id],
                        edge_type=EdgeType.DIRECTED,
                    )
                    dag_edges.add(dag_edge)
        if len(dag_edges) > 0:
            dag = Tree.from_edgeset(dag_edges)
        else:
            dag = None
        return dag

    def is_parent_of(self, parent: Node, child: Node):
        """!"""

        def cond(n_1: Node, n_2: Node, e: Edge):
            """"""
            if e.type() == EdgeType.DIRECTED:
                c1 = n_1 == e.start() and e.end() == n_2
                return c1
            else:
                c1 = n_1 == e.start() and e.end() == n_2
                c2 = n_2 == e.start() and e.end() == n_1
                return c1 or c2

        return self.is_related_to(n1=parent, n2=child, condition=cond)

    def is_child_of(self, child: Node, parent: Node):
        """!"""
        return self.is_parent_of(n1=parent, n2=child)
