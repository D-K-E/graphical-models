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

    def moralize(self) -> PGModel:
        """!
        Moralize given chain graph
        """
        raise NotImplementedError

    def get_chain_components(self) -> Set[UndiGraph]:
        """!
        Based on the equivalent relation defined by Drton 2009
        and the answer in so: https://stackoverflow.com/a/14518552/7330813
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
