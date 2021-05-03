# Usage Examples

## PGModel Usage


`PGModel`, a graph with defined as `G=(V,E,F)` where `V` is vertex set composed
of `NumCatRVariable`s which are numeric categorical random variables, `E` is
edge set, and `F` is factor set. If `F` is none the factor set is deduced from
edge set where each edge is considered as a factor whose scope is the set of
incident nodes to edge. Sum-Product and Max-Product variable elimination are
supported by `PGModel`. Evidence encoded in nodes are directly used for
reducing factors during the instantiation of `PGModel`. Additional evidence can
be provided at query time as well for conditional and most probable explanation
queries. `Marginal Map` queries are not yet supported.

Usage:

\code{.py}

from gmodels.pgmodel import PGModel
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.factor import Factor
from gmodels.randomvariable import NumCatRVariable
# Example adapted from Darwiche 2009, p. 140
idata = {
            "a": {"outcome-values": [True, False]},
            "b": {"outcome-values": [True, False]},
            "c": {"outcome-values": [True, False]},
        }
a = NumCatRVariable(
            node_id="a", input_data=idata["a"], marginal_distribution=lambda x: 0.6 if x else 0.4
        )
b = NumCatRVariable(
    node_id="b", input_data=idata["b"], marginal_distribution=lambda x: 0.5 if x else 0.5
)
c = NumCatRVariable(
    node_id="c", input_data=idata["c"], marginal_distribution=lambda x: 0.5 if x else 0.5
)
ab = Edge(
    edge_id="ab",
    edge_type=EdgeType.UNDIRECTED,
    start_node=a,
    end_node=b,
)
bc = Edge(
    edge_id="bc",
    edge_type=EdgeType.UNDIRECTED,
    start_node=b,
    end_node=c,
)
def phi_ba(scope_product):
    ""
    ss = set(scope_product)
    if ss == set([("a", True), ("b", True)]):
        return 0.9
    elif ss == set([("a", True), ("b", False)]):
        return 0.1
    elif ss == set([("a", False), ("b", True)]):
        return 0.2
    elif ss == set([("a", False), ("b", False)]):
        return 0.8
    else:
        raise ValueError("product error")

def phi_cb(scope_product):
    ""
    ss = set(scope_product)
    if ss == set([("c", True), ("b", True)]):
        return 0.3
    elif ss == set([("c", True), ("b", False)]):
        return 0.5
    elif ss == set([("c", False), ("b", True)]):
        return 0.7
    elif ss == set([("c", False), ("b", False)]):
        return 0.5
    else:
        raise ValueError("product error")

def phi_a(scope_product):
    s = set(scope_product)
    if s == set([("a", True)]):
        return 0.6
    elif s == set([("a", False)]):
        return 0.4
    else:
        raise ValueError("product error")
ba_f = Factor(gid="ba", scope_vars=set([b, a]), factor_fn=phi_ba)
cb_f = Factor(gid="cb", scope_vars=set([c, b]), factor_fn=phi_cb)
a_f = Factor(gid="a", scope_vars=set([a]), factor_fn=phi_a)
pgm = PGModel(
    gid="pgm",
    nodes=set([a, b, c]),
    edges=set([ab, bc]),
    factors=set([ba_f, cb_f, a_f]),
)
evidences = set([("a", True)])
queries = set([c])
product_factor, a = pgm.cond_prod_by_variable_elimination(queries, evidences)
print(round( product_factor.phi_normal(set([("c", True)])), 4))
# should give you 0.32

\endcode

## Bayesian Network Usage

Bayesian Network is defined by Koller, Friedman 2009, p. 57 as:
<blockquote>
Bayesian network structure G is a directed acyclic graph whose nodes represent
random variables \f$X1, \dots, Xn \f$ . Let \f$PaG(Xi)\f$ denote the parents
of \f$Xi\f$ in G, and `NonDescendants(Xi)` denote the variables in the graph
that are not descendants of Xi. Then G encodes the following set of
conditional independence assumptions, called the local independencies, and
denoted by `I(G): For each variable Xi : (Xi ⊥ NonDescendants(Xi) | PaG(Xi))`.
</blockquote>

Bayesian Network is defined by Koller, Friedman 2009, p. 62 as:
<blockquote>
Bayesian Network is a pair `B=(G, P)` where P factorizes over G, and where P
is specified as a set of CPDs associated with G’s nodes. The distribution P is
often annotated Pb. Let G be a BN structure over a set of random variables X ,
and let P be a joint distribution over the same space. If G is an I-map for P
, then P factorizes according to G:
`P(X1, \dots, Xn) = \prods_{i=0}^{n}P(Xi | PaG(Xi) )`
</blockquote>

Usage:

\code{.py}

idata = {"outcome-values": [True, False]}
                                                              
C = NumCatRVariable(
    node_id="C", input_data=idata, distribution=lambda x: 0.5
)
E = NumCatRVariable(
    node_id="E", input_data=idata, distribution=lambda x: 0.5
)
F = NumCatRVariable(
    node_id="F", input_data=idata, distribution=lambda x: 0.5
)
D = NumCatRVariable(
    node_id="D", input_data=idata, distribution=lambda x: 0.5
)
CE = Edge(
  edge_id="CE",
  start_node=C,
  end_node=E,
  edge_type=EdgeType.DIRECTED,
)
ED = Edge(
    edge_id="ED",
    start_node=E,
    end_node=D,
    edge_type=EdgeType.DIRECTED,
)
EF = Edge(
    edge_id="EF",
    start_node=E,
    end_node=F,
    edge_type=EdgeType.DIRECTED,
)
                                                              
def phi_c(scope_product):
    ss = set(scope_product)
   if ss == set([("C", True)]):
       return 0.8
    elif ss == set([("C", False)]):
        return 0.2
    else:
        raise ValueError("scope product unknown")
                                                              
def phi_ec(scope_product):
    ss = set(scope_product)
    if ss == set([("C", True), ("E", True)]):
        return 0.9
    elif ss == set([("C", True), ("E", False)]):
        return 0.1
  elif ss == set([("C", False), ("E", True)]):
      return 0.7
  elif ss == set([("C", False), ("E", False)]):
      return 0.3
  else:
       raise ValueError("scope product unknown")
                                                              
def phi_fe(scope_product):
  ss = set(scope_product)
  if ss == set([("E", True), ("F", True)]):
      return 0.9
  elif ss == set([("E", True), ("F", False)]):
      return 0.1
  elif ss == set([("E", False), ("F", True)]):
        return 0.5
    elif ss == set([("E", False), ("F", False)]):
        return 0.5
    else:
        raise ValueError("scope product unknown")
                                                              
def phi_de(scope_product):
    ss = set(scope_product)
  if ss == set([("E", True), ("D", True)]):
      return 0.7
  elif ss == set([("E", True), ("D", False)]):
      return 0.3
  elif ss == set([("E", False), ("D", True)]):
      return 0.4
  elif ss == set([("E", False), ("D", False)]):
      return 0.6
   else:
       raise ValueError("scope product unknown")
                                                              
CE_f = Factor(
    gid="CE_f", scope_vars=set([C, E]), factor_fn=phi_ec
)
C_f = Factor(gid="C_f", scope_vars=set([C]), factor_fn=phi_c)
FE_f = Factor(
    gid="FE_f", scope_vars=set([F, E]), factor_fn=phi_fe
)
DE_f = Factor(
    gid="DE_f", scope_vars=set([D, E]), factor_fn=phi_de
)
bayes_n = BayesianNetwork(
    gid="ba",
    nodes=set([C, E, D, F]),
    edges=set([EF, CE, ED]),
    factors=set([C_f, DE_f, CE_f, FE_f]),
)
query_vars = set([self.E])
evidences = set([("F", True)])
probs, alpha = self.bayes_n.cond_prod_by_variable_elimination(
    query_vars, evidences=evidences
)
query_value = set([("E", True)])
round(probs.phi(pss), 4)
# 0.774

\endcode


## Markov Network Usage

Markov Network is defined by Koller, Friedman 2009, p. 103 is
<blockquote>
As in a Bayesian network, the nodes in the graph of a Markov network represent
the variables, and the edges correspond to a notion of direct probabilistic
interaction between the neighboring variables — an interaction that is not
mediated by any other variable in the network.
</blockquote>

Usage:

\code{.py}

from gmodels.markov import MarkovNetwork
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.factor import Factor
from gmodels.randomvariable import NumCatRVariable


idata = {
    "A": {"outcome-values": [True, False]},
    "B": {"outcome-values": [True, False]},
    "C": {"outcome-values": [True, False]},
    "D": {"outcome-values": [True, False]},
}
                                                                   
# misconception example: Koller, Friedman, 2009 p. 104

A = NumCatRVariable(
    node_id="A", input_data=idata["A"], marginal_distribution=lambda x: 0.5
)
B = NumCatRVariable(
    node_id="B", input_data=idata["B"], marginal_distribution=lambda x: 0.5
)
C = NumCatRVariable(
    node_id="C", input_data=idata["C"], marginal_distribution=lambda x: 0.5
)
D = NumCatRVariable(
    node_id="D", input_data=idata["D"], marginal_distribution=lambda x: 0.5
)
AB = Edge(
    edge_id="AB",
    edge_type=EdgeType.UNDIRECTED,
    start_node=A,
    end_node=B,
)
AD = Edge(
    edge_id="AD",
    edge_type=EdgeType.UNDIRECTED,
    start_node=A,
    end_node=D,
)
DC = Edge(
    edge_id="DC",
    edge_type=EdgeType.UNDIRECTED,
    start_node=D,
    end_node=C,
)
BC = Edge(
    edge_id="BC",
    edge_type=EdgeType.UNDIRECTED,
    start_node=B,
    end_node=C,
)
                                                                   
def phi_AB(scope_product):
    ""
    ss = frozenset(scope_product)
    if ss == frozenset([("A", False), ("B", False)]):
        return 30.0
    elif ss == frozenset([("A", False), ("B", True)]):
        return 5.0
    elif ss == frozenset([("A", True), ("B", False)]):
        return 1.0
    elif ss == frozenset([("A", True), ("B", True)]):
        return 10.0
    else:
        raise ValueError("product error")
                                                                   
def phi_BC(scope_product):
    ""
    ss = frozenset(scope_product)
    if ss == frozenset([("B", False), ("C", False)]):
        return 100.0
    elif ss == frozenset([("B", False), ("C", True)]):
        return 1.0
    elif ss == frozenset([("B", True), ("C", False)]):
        return 1.0
    elif ss == frozenset([("B", True), ("C", True)]):
        return 100.0
    else:
        raise ValueError("product error")
                                                                   
def phi_CD(scope_product):
    ""
    ss = frozenset(scope_product)
    if ss == frozenset([("C", False), ("D", False)]):
        return 1.0
    elif ss == frozenset([("C", False), ("D", True)]):
        return 100.0
    elif ss == frozenset([("C", True), ("D", False)]):
        return 100.0
    elif ss == frozenset([("C", True), ("D", True)]):
        return 1.0
    else:
        raise ValueError("product error")
                                                                   
def phi_DA(scope_product):
    ""
    ss = frozenset(scope_product)
    if ss == frozenset([("D", False), ("A", False)]):
        return 100.0
    elif ss == frozenset([("D", False), ("A", True)]):
        return 1.0
    elif ss == frozenset([("D", True), ("A", False)]):
        return 1.0
    elif ss == frozenset([("D", True), ("A", True)]):
        return 100.0
    else:
        raise ValueError("product error")
                                                                   
AB_f = Factor(
    gid="ab_f", scope_vars=set([A, B]), factor_fn=phi_AB
)
BC_f = Factor(
    gid="bc_f", scope_vars=set([B, C]), factor_fn=phi_BC
)
CD_f = Factor(
    gid="cd_f", scope_vars=set([C, D]), factor_fn=phi_CD
)
DA_f = Factor(
    gid="da_f", scope_vars=set([D, A]), factor_fn=phi_DA
)
                                                                   
mnetwork = MarkovNetwork(
    gid="mnet",
    nodes=set([A, B, C, D]),
    edges=set([AB, AD, BC, DC]),
    factors=set([DA_f, CD_f, BC_f, AB_f]),
)

query_vars = set([A, B])
q2 = set([("A", False), ("B", True)])
round(prob.phi_normal(q2), 2)
# 0.69

\endcode

## Conditional Random Fields (CRFs) Usage

Conditional random fields are defined by Koller, Friedman 2009 p. 143 as:
<blockquote>
an undirected graph whose nodes correspond to a union of a set of observed
random variables X, and a set of target random variables Y; the network is
annotated with a set of factors \f$\phi_1(D_1), \dots, \phi_i(D_i), \dots,
\phi_m(D_m)\f$ such that \f$D_i \not \subset X\f$.
</blockquote>
The network encodes a conditional distribution between target and observed
variables.

Usage:
\code{.py}

from gmodels.randomvariable import NumCatRVariable
from gmodels.markov import ConditionalRandomField
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.factor import Factor
import math
from random import choice

idata = {"A": {"outcome-values": [True, False]}}

# from Koller, Friedman 2009, p. 144-145, example 4.20
X_1 = NumCatRVariable(
    node_id="X_1", input_data=idata["A"], marginal_distribution=lambda x: 0.5
)
X_2 = NumCatRVariable(
    node_id="X_2", input_data=idata["A"], marginal_distribution=lambda x: 0.5
)
X_3 = NumCatRVariable(
    node_id="X_3", input_data=idata["A"], marginal_distribution=lambda x: 0.5
)
Y_1 = NumCatRVariable(
    node_id="Y_1", input_data=idata["A"], marginal_distribution=lambda x: 0.5
)
X1_Y1 = Edge(
   edge_id="X1_Y1",
   edge_type=EdgeType.UNDIRECTED,
   start_node=X_1,
   end_node=Y_1,
)
X2_Y1 = Edge(
  edge_id="X2_Y1",
  edge_type=EdgeType.UNDIRECTED,
  start_node=X_2,
  end_node=Y_1,
)
X3_Y1 = Edge(
  edge_id="X3_Y1",
  edge_type=EdgeType.UNDIRECTED,
  start_node=X_3,
  end_node=Y_1,
)
                                                                     
def phi_X1_Y1(scope_product):
  ""
  w = 0.5
  ss = frozenset(scope_product)
  if ss == frozenset([("X_1", True), ("Y_1", True)]):
      return math.exp(1.0 * w)
  else:
      return math.exp(0.0)
                                                                     
def phi_X2_Y1(scope_product):
  ""
  w = 5.0
  ss = frozenset(scope_product)
  if ss == frozenset([("X_2", True), ("Y_1", True)]):
      return math.exp(1.0 * w)
  else:
      return math.exp(0.0)
                                                                     
def phi_X3_Y1(scope_product):
  ""
  w = 9.4
  ss = frozenset(scope_product)
  if ss == frozenset([("X_3", True), ("Y_1", True)]):
      return math.exp(1.0 * w)
  else:
      return math.exp(0.0)
                                                                     
def phi_Y1(scope_product):
  ""
  w = 0.6
  ss = frozenset(scope_product)
  if ss == frozenset([("Y_1", True)]):
      return math.exp(1.0 * w)
  else:
      return math.exp(0.0)
                                                                     
X1_Y1_f = Factor(
    gid="x1_y1_f", scope_vars=set([X_1, Y_1]), factor_fn=phi_X1_Y1
)
X2_Y1_f = Factor(
    gid="x2_y1_f", scope_vars=set([X_2, Y_1]), factor_fn=phi_X2_Y1
)
X3_Y1_f = Factor(
    gid="x3_y1_f", scope_vars=set([X_3, Y_1]), factor_fn=phi_X3_Y1
)
Y1_f = Factor(gid="y1_f", scope_vars=set([Y_1]), factor_fn=phi_Y1)
                                                                     
crf_koller = ConditionalRandomField(
    "crf",
    observed_vars=set([X_1, X_2, X_3]),
    target_vars=set([Y_1]),
    edges=set([X1_Y1, X2_Y1, X3_Y1]),
    factors=set([X1_Y1_f, X2_Y1_f, X3_Y1_f, Y1_f]),
)
evidence = set([("Y_1", False)])
query = set(
    [
        ("X_1", choice([False, True])),
        ("X_2", choice([False, True])),
        ("X_3", choice([False, True])),
    ]
)
foo1, a1 = crf_koller.cond_prod_by_variable_elimination(
    queries=query, evidences=evidence
)
print(foo1.phi(query) == 1.0)
# True

\endcode


## LWF Chain Graph Usage

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

from gmodels.lwfchain import LWFChainGraph
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.factor import Factor
from gmodels.randomvariable import NumCatRVariable


idata = {"outcome-values": [True, False]}
A = NumCatRVariable(
       node_id="A", input_data=idata, marginal_distribution=lambda x: 0.5
)
B = NumCatRVariable(
       node_id="B", input_data=idata, marginal_distribution=lambda x: 0.5
)
C = NumCatRVariable(
       node_id="C", input_data=idata, marginal_distribution=lambda x: 0.5
)
D = NumCatRVariable(
       node_id="D", input_data=idata, marginal_distribution=lambda x: 0.5
)
E = NumCatRVariable(
       node_id="E", input_data=idata, marginal_distribution=lambda x: 0.5
)
F = NumCatRVariable(
       node_id="F", input_data=idata, marginal_distribution=lambda x: 0.5
)
G = NumCatRVariable(
       node_id="G", input_data=idata, marginal_distribution=lambda x: 0.5
)
H = NumCatRVariable(
       node_id="H", input_data=idata, marginal_distribution=lambda x: 0.5
)
I = NumCatRVariable(
       node_id="I", input_data=idata, marginal_distribution=lambda x: 0.5
)
K = NumCatRVariable(
       node_id="K", input_data=idata, marginal_distribution=lambda x: 0.5
)
L = NumCatRVariable(
       node_id="L", input_data=idata, marginal_distribution=lambda x: 0.5
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
evidences = set([("E", True), ("A", True), ("G", False)])

final_factor, a = cowell.cond_prod_by_variable_elimination(
    set([B]), evidences
)

round(final_factor.phi_normal(set([("B", True)])), 4)
# 0.60

\endcode
