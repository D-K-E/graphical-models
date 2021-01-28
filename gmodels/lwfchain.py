"""!
Probabilistic Graphic Model - LWF Chain Graph

Partially Directed Acyclic Graph as in Koller, Friedman 2009, p. 37
"""
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.gtypes.node import Node
from gmodels.randomvariable import NumCatRVariable, NumericValue
from gmodels.factor import Factor
from gmodels.pgmodel import PGModel
from gmodels.gtypes.graph import Graph
from gmodels.gtypes.tree import Tree
from gmodels.gtypes.undigraph import UndiGraph
from typing import Callable, Set, List, Optional, Dict, Tuple
import math
from uuid import uuid4


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
        ""
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges, factors=factors)
        self.chain_components = {str(uuid4()): c for c in self.get_chain_components()}
        self.nb_components = (
            len(self.chain_components) if len(self.chain_components) != 0 else 1
        )
        self.dag_components = self.get_chain_dag()

    def moralize(self) -> PGModel:
        """!
        Moralize given chain graph
        """
        raise NotImplementedError

    def get_chain_components(self) -> Set[UndiGraph]:
        """!
        Based on the equivalence relation defined by Drton 2009
        and the answer in so: https://stackoverflow.com/a/14518552/7330813

        The equivalence relation: Define two vertices \fv_0\f and \fv_k\f in a
        chain graph G to be equivalent if there exists a path \f(v_0,...,
        v_k)\f such that \fv_i − v_{i+1}\f in G for all 0 ≤ i ≤ k − 1. The
        equivalence classes under this equivalence relation are the chain
        components of G.
        Basically the connected components of an undirected graph whose
        vertices are incident with undirected edges of the given chain graph.
        """
        edges = set()
        for e in self.edges():
            if e.type() == EdgeType.UNDIRECTED:
                edges.add(e)

        g = Graph.from_edgeset(edges)
        undi = UndiGraph.from_graph(g)
        chain_components: Set[UndiGraph] = set()
        for cg in undi.get_components():
            component = UndiGraph.from_graph(cg)
            chain_components.add(component)
        return chain_components

    def get_chain_component_factors(self) -> Dict[str, Set[Factor]]:
        ""
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
            if estart in component.nodes():
                start_component_id = cid
            if eend in component.nodes():
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
                node_id=cid, distribution=lambda x: 1.0 / self.nb_components
            )
            for cid in chain_factors
        }
        dag_edges = set()
        for e in self.edges():
            if e.type() == EdgeType.DIRECTED:
                (
                    edge_between_components_check,
                    start_component_id,
                    end_component_id,
                ) = self.check_edge_between_components(e)
                if edge_between_components_check is True:
                    dag_edge = Edge(
                        edge_id=str(uuid4()),
                        start_node=dag_nodes[start_component_id],
                        end_node=dag_nodes[end_component_id],
                        edge_type=EdgeType.DIRECTED,
                    )
                    dag_edges.add(dag_edge)
        dag = Tree.from_edgeset(dag_edges)
        return dag

    def is_parent_of(self, parent: Node, child: Node):
        """!
        """

        def cond(n_1: Node, n_2: Node, e: Edge):
            ""
            c1 = n_1 == e.start() and e.end() == n_2
            c2 = c1 and e.type() == EdgeType.DIRECTED
            return c2

        return self.is_related_to(n1=parent, n2=child, condition=cond)

    def is_child_of(self, child: Node, parent: Node):
        """!
        """
        return self.is_parent_of(n1=parent, n2=child, condition=cond)
