"""!
Probabilistic Graphic Model - LWF Chain Graph

Partially Directed Acyclic Graph as in Koller, Friedman 2009, p. 37
"""
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.gtypes.node import Node
from gmodels.randomvariable import NumCatRVariable
from gmodels.factor import Factor
from gmodels.pgmodel import PGModel
from gmodels.markov import MarkovNetwork, ConditionalRandomField
from gmodels.gtypes.graph import Graph
from gmodels.gtypes.tree import Tree
from gmodels.gtypes.undigraph import UndiGraph
from typing import Set, Dict, Tuple, Union
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
        edges = self.edges()
        enodes = set([frozenset([e.start(), e.end()]) for e in edges])
        # add edges
        for cid in range(len(self.ccomponents)):
            pa_k_i: Set[NumCatRVariable] = self.parents_of_K(i=cid)
            pa_k_i_cp = set([p for p in pa_k_i])
            while len(pa_k_i_cp) > 0:
                parent_node = pa_k_i_cp.pop()
                for pnode in pa_k_i:
                    is_n_ind = self.is_node_independent_of(parent_node, pnode)
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
            gid=str(uuid4()), nodes=self.nodes(), edges=nedges, factors=self.factors()
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
        ""
        return set([self.component_to_crf(i) for i in range(len(self.ccomponents))])

    def chain_component(self, dag_id: str) -> Set[UndiGraph]:
        """!
        """
        return self.chain_components[dag_id]

    def K(self, i: int) -> Union[NumCatRVariable, UndiGraph]:
        """!
        From Koller, Friedman 2009, p. 148
        """
        return self.ccomponents[i]

    def K_nodes(self, i: int) -> Set[NumCatRVariable]:
        """!
        """
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
            knodes = K_i.nodes()
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
        ""
        return set(
            [
                n_p
                for n_p in self.nodes()
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
        for e in self.edges():
            if e.type() == EdgeType.UNDIRECTED:
                edges.add(e)

        undi = UndiGraph.from_graph(
            Graph.from_edge_node_set(edges=edges, nodes=self.nodes())
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
            if isinstance(component, UndiGraph) is True:
                cnodes = component.nodes()
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
                distribution=lambda x: 1.0 / self.nb_components,
            )
            for cid in self.chain_components
        }
        dag_edges = set()
        for e in self.edges():
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
        """!
        """

        def cond(n_1: Node, n_2: Node, e: Edge):
            ""
            if e.type() == EdgeType.DIRECTED:
                c1 = n_1 == e.start() and e.end() == n_2
                return c1
            else:
                c1 = n_1 == e.start() and e.end() == n_2
                c2 = n_2 == e.start() and e.end() == n_1
                return c1 or c2

        return self.is_related_to(n1=parent, n2=child, condition=cond)

    def is_child_of(self, child: Node, parent: Node):
        """!
        """
        return self.is_parent_of(n1=parent, n2=child)


"""!
\page lwfchaingraphexample LWF Chain Graph Usage

LWF Chain Graph, also known as Partially Directed Model, is a probabilistic
graphical model. It's distinctive nature is best explained by Koller, Friedman
2009, p. 148:
<blockquote>
An edge between two nodes in the same chain component must be undirected, while
an edge between two nodes in different chain components must be directed.
</blockquote>

S. Lauritzen, one of the main contributors (the L in LWF) of the subject, had
written extensively on the subject. However probably the most through treatment
of the subject is Lauritzen 1996, p. 158 - 220. He had also provided the causal
interpretation of LWF chain graphs in [Lauritzen 2002](http://doi.wiley.com/10.1111/1467-9868.00340).
The standard inference strategies on chain graphs are best explained in Cowell
2005 and more recently in Dechter 2019.

Usage:

\code{.py}

idata = {"outcome-values": [True, False]}
A = NumCatRVariable(
       node_id="A", input_data=idata, distribution=lambda x: 0.5
)
B = NumCatRVariable(
       node_id="B", input_data=idata, distribution=lambda x: 0.5
)
C = NumCatRVariable(
       node_id="C", input_data=idata, distribution=lambda x: 0.5
)
D = NumCatRVariable(
       node_id="D", input_data=idata, distribution=lambda x: 0.5
)
E = NumCatRVariable(
       node_id="E", input_data=idata, distribution=lambda x: 0.5
)
F = NumCatRVariable(
       node_id="F", input_data=idata, distribution=lambda x: 0.5
)
G = NumCatRVariable(
       node_id="G", input_data=idata, distribution=lambda x: 0.5
)
H = NumCatRVariable(
       node_id="H", input_data=idata, distribution=lambda x: 0.5
)
I = NumCatRVariable(
       node_id="I", input_data=idata, distribution=lambda x: 0.5
)
K = NumCatRVariable(
       node_id="K", input_data=idata, distribution=lambda x: 0.5
)
L = NumCatRVariable(
       node_id="L", input_data=idata, distribution=lambda x: 0.5
)
#
#  Cowell 2005, p. 110
#
#   A                      E---+
#   |                          |
#   +----+                 F <-+
#        |                 |
#   B <--+---> C --> D <---+
#   |                |
#   +---> H <--------+----> G
#   |     |
#   +---> I
#
AB_c = Edge(
  edge_id="AB",
  start_node=A,
  end_node=B,
  edge_type=EdgeType.DIRECTED,
)
AC_c = Edge(
  edge_id="AC",
  start_node=A,
  end_node=C,
  edge_type=EdgeType.DIRECTED,
)
CD_c = Edge(
  edge_id="CD",
  start_node=C,
  end_node=D,
  edge_type=EdgeType.DIRECTED,
)
EF_c = Edge(
  edge_id="EF",
  start_node=E,
  end_node=F,
  edge_type=EdgeType.DIRECTED,
)
FD_c = Edge(
  edge_id="FD",
  start_node=F,
  end_node=D,
  edge_type=EdgeType.DIRECTED,
)
DG_c = Edge(
  edge_id="DG",
  start_node=D,
  end_node=G,
  edge_type=EdgeType.DIRECTED,
)
DH_c = Edge(
  edge_id="DH",
  start_node=D,
  end_node=H,
  edge_type=EdgeType.DIRECTED,
)
BH_c = Edge(
  edge_id="BH",
  start_node=B,
  end_node=H,
  edge_type=EdgeType.DIRECTED,
)
BI_c = Edge(
  edge_id="BI",
  start_node=B,
  end_node=I,
  edge_type=EdgeType.DIRECTED,
)
HI_c = Edge(
  edge_id="HI",
  start_node=H,
  end_node=I,
  edge_type=EdgeType.UNDIRECTED,
)
#
# Factors
#
def phi_e(scope_product):
    "Visit to Asia factor p(a)
    "
    ss = set(scope_product)
    if ss == set([("E", True)]):
        return 0.01
    elif ss == set([("E", False)]):
        return 0.99
    else:
        raise ValueError("Unknown scope product")

E_cf = Factor(gid="E_cf", scope_vars=set([E]), factor_fn=phi_e)

def phi_fe(scope_product):
    "Tuberculosis | Visit to Asia factor p(t,a)"
    ss = set(scope_product)
    if ss == set([("F", True), ("E", True)]):
        return 0.05
    elif ss == set([("F", False), ("E", True)]):
        return 0.95
    elif ss == set([("F", True), ("E", False)]):
        return 0.01
    elif ss == set([("F", False), ("E", False)]):
        return 0.99
    else:
        raise ValueError("Unknown scope product")

EF_cf = Factor(
    gid="EF_cf", scope_vars=set([E, F]), factor_fn=phi_fe
)

def phi_dg(scope_product):
    "either tuberculosis or lung cancer | x ray p(e,x)"
    ss = set(scope_product)
    if ss == set([("D", True), ("G", True)]):
        return 0.98
    elif ss == set([("D", False), ("G", True)]):
        return 0.05
    elif ss == set([("D", True), ("G", False)]):
        return 0.02
    elif ss == set([("D", False), ("G", False)]):
        return 0.95
    else:
        raise ValueError("Unknown scope product")

DG_cf = Factor(
    gid="DG_cf", scope_vars=set([D, G]), factor_fn=phi_dg
)

def phi_a(scope_product):
    "smoke factor p(s)"
    ss = set(scope_product)
    if ss == set([("A", True)]):
        return 0.5
    elif ss == set([("A", False)]):
        return 0.5
    else:
        raise ValueError("Unknown scope product")

A_cf = Factor(gid="A_cf", scope_vars=set([A]), factor_fn=phi_a)

def phi_ab(scope_product):
    "smoke given bronchitis p(s,b)"
    ss = set(scope_product)
    if ss == set([("A", True), ("B", True)]):
        return 0.6
    elif ss == set([("A", False), ("B", True)]):
        return 0.3
    elif ss == set([("A", True), ("B", False)]):
        return 0.4
    elif ss == set([("A", False), ("B", False)]):
        return 0.7
    else:
        raise ValueError("Unknown scope product")

AB_cf = Factor(
    gid="AB_cf", scope_vars=set([A, B]), factor_fn=phi_ab
)

def phi_ac(scope_product):
    "lung cancer given smoke p(s,l)"
    ss = set(scope_product)
    if ss == set([("A", True), ("C", True)]):
        return 0.1
    elif ss == set([("A", False), ("C", True)]):
        return 0.01
    elif ss == set([("A", True), ("C", False)]):
        return 0.9
    elif ss == set([("A", False), ("C", False)]):
        return 0.99
    else:
        raise ValueError("Unknown scope product")

AC_cf = Factor(
    gid="AC_cf", scope_vars=set([A, C]), factor_fn=phi_ac
)

def phi_cdf(scope_product):
    "either tuberculosis or lung given lung cancer and tuberculosis p(e, l, t)"
    ss = set(scope_product)
    if ss == set([("C", True), ("D", True), ("F", True)]):
        return 1
    elif ss == set([("C", True), ("D", False), ("F", True)]):
        return 0
    elif ss == set([("C", False), ("D", True), ("F", True)]):
        return 1
    elif ss == set([("C", False), ("D", False), ("F", True)]):
        return 0
    elif ss == set([("C", True), ("D", True), ("F", False)]):
        return 1
    elif ss == set([("C", True), ("D", False), ("F", False)]):
        return 0
    elif ss == set([("C", False), ("D", True), ("F", False)]):
        return 0
    elif ss == set([("C", False), ("D", False), ("F", False)]):
        return 1
    else:
        raise ValueError("Unknown scope product")

CDF_cf = Factor(
    gid="CDF_cf", scope_vars=set([D, C, F]), factor_fn=phi_cdf
)

def phi_ihb(scope_product):
    "cough, dyspnoea, bronchitis I, H, B p(c,d,b)"
    ss = set(scope_product)
    if ss == set([("H", True), ("I", True), ("B", True)]):
        return 16
    elif ss == set([("H", True), ("I", False), ("B", True)]):
        return 1
    elif ss == set([("H", False), ("I", True), ("B", True)]):
        return 4
    elif ss == set([("H", False), ("I", False), ("B", True)]):
        return 1
    elif ss == set([("H", True), ("I", True), ("B", False)]):
        return 2
    elif ss == set([("H", True), ("I", False), ("B", False)]):
        return 1
    elif ss == set([("H", False), ("I", True), ("B", False)]):
        return 1
    elif ss == set([("H", False), ("I", False), ("B", False)]):
        return 1
    else:
        raise ValueError("Unknown scope product")

IHB_cf = Factor(
    gid="IHB_cf", scope_vars=set([H, I, B]), factor_fn=phi_ihb
)

def phi_hbd(scope_product):
    "cough, either tuberculosis or lung cancer, bronchitis D, H, B p(c,b,e)"
    ss = set(scope_product)
    if ss == set([("H", True), ("D", True), ("B", True)]):
        return 5
    elif ss == set([("H", True), ("D", False), ("B", True)]):
        return 2
    elif ss == set([("H", False), ("D", True), ("B", True)]):
        return 1
    elif ss == set([("H", False), ("D", False), ("B", True)]):
        return 1
    elif ss == set([("H", True), ("D", True), ("B", False)]):
        return 3
    elif ss == set([("H", True), ("D", False), ("B", False)]):
        return 1
    elif ss == set([("H", False), ("D", True), ("B", False)]):
        return 1
    elif ss == set([("H", False), ("D", False), ("B", False)]):
        return 1
    else:
        raise ValueError("Unknown scope product")

HBD_cf = Factor(
    gid="HBD_cf", scope_vars=set([H, D, B]), factor_fn=phi_hbd
)

def phi_bd(scope_product):
    "bronchitis, either tuberculosis or lung cancer B, D p(b,e)"
    ss = set(scope_product)
    if ss == set([("B", True), ("D", True)]):
        return 1 / 90
    elif ss == set([("B", False), ("D", True)]):
        return 1 / 11
    elif ss == set([("B", True), ("D", False)]):
        return 1 / 39
    elif ss == set([("B", False), ("D", False)]):
        return 1 / 5
    else:
        raise ValueError("Unknown scope product")

BD_cf = Factor(
    gid="BD_cf", scope_vars=set([D, B]), factor_fn=phi_bd
)

cowell = LWFChainGraph(
    gid="cowell",
    nodes=set([A, B, C, D, E, F, G, H, I]),
    edges=set([AB_c, AC_c, CD_c, EF_c, FD_c, DG_c, DH_c, BH_c, BI_c, HI_c]),
    factors=set([E_cf, EF_cf, DG_cf, A_cf, AB_cf, AC_cf, CDF_cf, IHB_cf, HBD_cf, 
        BD_cf])
)

\endcode

"""

