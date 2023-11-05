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

# import necessary packages
from pygmodels.pgm.pgmtype.pgmodel import PGModel
from pygmodels.graph.gtype.edge import Edge, EdgeType
from pygmodels.factor.factor import Factor
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable
from pygmodels.factor.factorf.factorops import FactorOps

# Example adapted from Darwiche 2009, p. 140

# define data
idata = {
            "a": {"outcome-values": [True, False]},
            "b": {"outcome-values": [True, False]},
            "c": {"outcome-values": [True, False]},
        }

# define nodes
a = NumCatRVariable(
            node_id="a", input_data=idata["a"], marginal_distribution=lambda x: 0.6 if x else 0.4
        )
b = NumCatRVariable(
    node_id="b", input_data=idata["b"], marginal_distribution=lambda x: 0.5 if x else 0.5
)
c = NumCatRVariable(
    node_id="c", input_data=idata["c"], marginal_distribution=lambda x: 0.5 if x else 0.5
)

# define edges
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

# define factor functions
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
        
# instantiate factors with factor functions and random variables in scope
ba_f = Factor(gid="ba", scope_vars=set([b, a]), factor_fn=phi_ba)
cb_f = Factor(gid="cb", scope_vars=set([c, b]), factor_fn=phi_cb)
a_f = Factor(gid="a", scope_vars=set([a]), factor_fn=phi_a)

# Instantiate the graph with nodes, edges and factors and do a query with given evidence
pgm = PGModel(
    gid="pgm",
    nodes=set([a, b, c]),
    edges=set([ab, bc]),
    factors=set([ba_f, cb_f, a_f]),
)
evidences = set([("a", True)])
queries = set([c])
product_factor, a = pgm.cond_prod_by_variable_elimination(queries, evidences)
print(round( FactorOps.phi_normal(product_factor, set([("c", True)])), 4))
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

# import necessary parts

from pygmodels.pgm.pgmodel.bayesian import BayesianNetwork
from pygmodels.graph.gtype.edge import Edge, EdgeType
from pygmodels.factor.factor import Factor
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable

# data and nodes
idata = {"outcome-values": [True, False]}
                                                              
C = NumCatRVariable(
    node_id="C", input_data=idata, marginal_distribution=lambda x: 0.5
)
E = NumCatRVariable(
    node_id="E", input_data=idata, marginal_distribution=lambda x: 0.5
)
F = NumCatRVariable(
    node_id="F", input_data=idata, marginal_distribution=lambda x: 0.5
)
D = NumCatRVariable(
    node_id="D", input_data=idata, marginal_distribution=lambda x: 0.5
)

# edges
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

# define factor functions

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


# instantiate factors with given factor function and implied random variables                                                         
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
query_vars = set([E])
evidences = set([("F", True)])
probs, alpha = bayes_n.cond_prod_by_variable_elimination(
    query_vars, evidences=evidences
)
query_value = set([("E", True)])
round(probs.phi(query_value), 4)
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

# import necessary packages
from pygmodels.pgm.pgmodel.markov import MarkovNetwork
from pygmodels.graph.gtype.edge import Edge, EdgeType
from pygmodels.factor.factor import Factor
from pygmodels.factor.factorf.factorops import FactorOps
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable

# define data and random variable nodes
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

# define edges
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

# define factor functions

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

# instantiate factors with factor functions and implied
# random variables in scope 

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

# instantiate markov network and make a query
mnetwork = MarkovNetwork(
    gid="mnet",
    nodes=set([A, B, C, D]),
    edges=set([AB, AD, BC, DC]),
    factors=set([DA_f, CD_f, BC_f, AB_f]),
)
 
queries = set([A, B])
evidences = set()
f, a = mnetwork.cond_prod_by_variable_elimination(queries, evidences)
q2 = set([("A", False), ("B", True)])
round(FactorOps.phi_normal(f, q2), 2)
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

# import necessary packages
import math
from random import choice
from pygmodels.pgm.pgmodel.markov import ConditionalRandomField
from pygmodels.graph.gtype.edge import Edge, EdgeType
from pygmodels.factor.factor import Factor
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable

# define data and nodes
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

# define edges

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

# define factor functions

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

# instantiate factors with factor functions and implied random variables
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


# Instantiate conditional random field and make a query
crf_koller = ConditionalRandomField(
    "crf",
    observed_vars=set([X_1, X_2, X_3]),
    target_vars=set([Y_1]),
    edges=set([X1_Y1, X2_Y1, X3_Y1]),
    factors=set([X1_Y1_f, X2_Y1_f, X3_Y1_f, Y1_f]),
)
evidence = set([("Y_1", False)])
query_vars = set([X_1, X_2, X_3])
query = frozenset(
    [
        ("X_1", choice([False, True])),
        ("X_2", choice([False, True])),
        ("X_3", choice([False, True])),
    ]
)
fact, a1 = crf_koller.cond_prod_by_variable_elimination(
    queries=query_vars, evidences=evidence
)
print(fact.phi(query) == 1.0)
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

# import necessary packages
from pygmodels.pgm.pgmodel.lwfchain import LWFChainGraph
from pygmodels.pgm.pgmodel.bayesian import BayesianNetwork
from pygmodels.graph.gtype.edge import Edge, EdgeType
from pygmodels.factor.factor import Factor
from pygmodels.factor.factorf.factorops import FactorOps
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable


# define data and nodes
idata = {"outcome-values": [True, False]}
Smoking = NumCatRVariable(
       node_id="Smoking", input_data=idata, marginal_distribution=lambda x: 0.5
)
Bronchitis = NumCatRVariable(
       node_id="Bronchitis", input_data=idata, marginal_distribution=lambda x: 0.5
)
LungCancer = NumCatRVariable(
       node_id="LungCancer", input_data=idata, marginal_distribution=lambda x: 0.5
)
EitherTL = NumCatRVariable(
       node_id="EitherTL", input_data=idata, marginal_distribution=lambda x: 0.5
)
VisitAsia = NumCatRVariable(
       node_id="VisitAsia", input_data=idata, marginal_distribution=lambda x: 0.5
)
Tuberculosis = NumCatRVariable(
       node_id="Tuberculosis", input_data=idata, marginal_distribution=lambda x: 0.5
)
Xray = NumCatRVariable(
       node_id="Xray", input_data=idata, marginal_distribution=lambda x: 0.5
)
Cough = NumCatRVariable(
       node_id="Cough", input_data=idata, marginal_distribution=lambda x: 0.5
)
Dysponea = NumCatRVariable(
       node_id="Dysponea", input_data=idata, marginal_distribution=lambda x: 0.5
)

# define edges
#
#  Cowell 2005, p. 110
#
SmokingBronchitis_c = Edge(
  edge_id="SmokingBronchitis",
  start_node=Smoking,
  end_node=Bronchitis,
  edge_type=EdgeType.DIRECTED,
)
SmokingLungCancer_c = Edge(
  edge_id="SmokingLungCancer",
  start_node=Smoking,
  end_node=LungCancer,
  edge_type=EdgeType.DIRECTED,
)
LungCancerEitherTL_c = Edge(
  edge_id="LungCancerEitherTL",
  start_node=LungCancer,
  end_node=EitherTL,
  edge_type=EdgeType.DIRECTED,
)
VisitAsiaTuberculosis_c = Edge(
  edge_id="VisitAsiaF",
  start_node=VisitAsia,
  end_node=Tuberculosis,
  edge_type=EdgeType.DIRECTED,
)
TuberculosisEitherTL_c = Edge(
  edge_id="TuberculosisEitherTL",
  start_node=Tuberculosis,
  end_node=EitherTL,
  edge_type=EdgeType.DIRECTED,
)
EitherTLXray_c = Edge(
  edge_id="EitherTLXray",
  start_node=EitherTL,
  end_node=Xray,
  edge_type=EdgeType.DIRECTED,
)
EitherTLCough_c = Edge(
  edge_id="EitherTLCough",
  start_node=EitherTL,
  end_node=Cough,
  edge_type=EdgeType.DIRECTED,
)
BronchitisCough_c = Edge(
  edge_id="BronchitisCough",
  start_node=Bronchitis,
  end_node=Cough,
  edge_type=EdgeType.DIRECTED,
)
BronchitisDysponea_c = Edge(
  edge_id="BronchitisI",
  start_node=Bronchitis,
  end_node=Dysponea,
  edge_type=EdgeType.DIRECTED,
)
CoughDysponea_c = Edge(
  edge_id="CoughI",
  start_node=Cough,
  end_node=Dysponea,
  edge_type=EdgeType.UNDIRECTED,
)

# define factor functions

def phi_VisitAsia(scope_product):
    "Visit to Asia factor p(a)"
    ss = set(scope_product)
    if ss == set([("VisitAsia", True)]):
        return 0.01
    elif ss == set([("VisitAsia", False)]):
        return 0.99
    else:
        raise ValueError("Unknown scope product")

def phi_TuberculosisVisitAsia(scope_product):
    "Tuberculosis | Visit to Asia factor p(t,a)"
    ss = set(scope_product)
    if ss == set([("Tuberculosis", True), ("VisitAsia", True)]):
        return 0.05
    elif ss == set([("Tuberculosis", False), ("VisitAsia", True)]):
        return 0.95
    elif ss == set([("Tuberculosis", True), ("VisitAsia", False)]):
        return 0.01
    elif ss == set([("Tuberculosis", False), ("VisitAsia", False)]):
        return 0.99
    else:
        raise ValueError("Unknown scope product")


def phi_EitherTLXray(scope_product):
    "either tuberculosis or lung cancer | x ray p(e,x)"
    ss = set(scope_product)
    if ss == set([("EitherTL", True), ("Xray", True)]):
        return 0.98
    elif ss == set([("EitherTL", False), ("Xray", True)]):
        return 0.05
    elif ss == set([("EitherTL", True), ("Xray", False)]):
        return 0.02
    elif ss == set([("EitherTL", False), ("Xray", False)]):
        return 0.95
    else:
        raise ValueError("Unknown scope product")

def phi_Smoking(scope_product):
    "smoke factor p(s)"
    ss = set(scope_product)
    if ss == set([("Smoking", True)]):
        return 0.5
    elif ss == set([("Smoking", False)]):
        return 0.5
    else:
        raise ValueError("Unknown scope product")


def phi_SmokingBronchitis(scope_product):
    "smoke given bronchitis p(s,b)"
    ss = set(scope_product)
    if ss == set([("Smoking", True), ("Bronchitis", True)]):
        return 0.6
    elif ss == set([("Smoking", False), ("Bronchitis", True)]):
        return 0.3
    elif ss == set([("Smoking", True), ("Bronchitis", False)]):
        return 0.4
    elif ss == set([("Smoking", False), ("Bronchitis", False)]):
        return 0.7
    else:
        raise ValueError("Unknown scope product")


def phi_SmokingLungCancer(scope_product):
    "lung cancer given smoke p(s,l)"
    ss = set(scope_product)
    if ss == set([("Smoking", True), ("LungCancer", True)]):
        return 0.1
    elif ss == set([("Smoking", False), ("LungCancer", True)]):
        return 0.01
    elif ss == set([("Smoking", True), ("LungCancer", False)]):
        return 0.9
    elif ss == set([("Smoking", False), ("LungCancer", False)]):
        return 0.99
    else:
        raise ValueError("Unknown scope product")


def phi_LungCancerEitherTLTuberculosis(scope_product):
    "either tuberculosis or lung given lung cancer and tuberculosis p(e, l, t)"
    ss = set(scope_product)
    if ss == set([("LungCancer", True), ("EitherTL", True), ("Tuberculosis", True)]):
        return 1
    elif ss == set([("LungCancer", True), ("EitherTL", False), ("Tuberculosis", True)]):
        return 0
    elif ss == set([("LungCancer", False), ("EitherTL", True), ("Tuberculosis", True)]):
        return 1
    elif ss == set([("LungCancer", False), ("EitherTL", False), ("Tuberculosis", True)]):
        return 0
    elif ss == set([("LungCancer", True), ("EitherTL", True), ("Tuberculosis", False)]):
        return 1
    elif ss == set([("LungCancer", True), ("EitherTL", False), ("Tuberculosis", False)]):
        return 0
    elif ss == set([("LungCancer", False), ("EitherTL", True), ("Tuberculosis", False)]):
        return 0
    elif ss == set([("LungCancer", False), ("EitherTL", False), ("Tuberculosis", False)]):
        return 1
    else:
        raise ValueError("Unknown scope product")


def phi_DysponeaCoughBronchitis(scope_product):
    "cough, dyspnoea, bronchitis I, H, B p(c,d,b)"
    ss = set(scope_product)
    if ss == set([("Cough", True), ("Dysponea", True), ("Bronchitis", True)]):
        return 16
    elif ss == set([("Cough", True), ("Dysponea", False), ("Bronchitis", True)]):
        return 1
    elif ss == set([("Cough", False), ("Dysponea", True), ("Bronchitis", True)]):
        return 4
    elif ss == set([("Cough", False), ("Dysponea", False), ("Bronchitis", True)]):
        return 1
    elif ss == set([("Cough", True), ("Dysponea", True), ("Bronchitis", False)]):
        return 2
    elif ss == set([("Cough", True), ("Dysponea", False), ("Bronchitis", False)]):
        return 1
    elif ss == set([("Cough", False), ("Dysponea", True), ("Bronchitis", False)]):
        return 1
    elif ss == set([("Cough", False), ("Dysponea", False), ("Bronchitis", False)]):
        return 1
    else:
        raise ValueError("Unknown scope product")


def phi_CoughBronchitisEitherTL(scope_product):
    "cough, either tuberculosis or lung cancer, bronchitis D, H, B p(c,b,e)"
    ss = set(scope_product)
    if ss == set([("Cough", True), ("EitherTL", True), ("Bronchitis", True)]):
        return 5
    elif ss == set([("Cough", True), ("EitherTL", False), ("Bronchitis", True)]):
        return 2
    elif ss == set([("Cough", False), ("EitherTL", True), ("Bronchitis", True)]):
        return 1
    elif ss == set([("Cough", False), ("EitherTL", False), ("Bronchitis", True)]):
        return 1
    elif ss == set([("Cough", True), ("EitherTL", True), ("Bronchitis", False)]):
        return 3
    elif ss == set([("Cough", True), ("EitherTL", False), ("Bronchitis", False)]):
        return 1
    elif ss == set([("Cough", False), ("EitherTL", True), ("Bronchitis", False)]):
        return 1
    elif ss == set([("Cough", False), ("EitherTL", False), ("Bronchitis", False)]):
        return 1
    else:
        raise ValueError("Unknown scope product")


def phi_BronchitisEitherTL(scope_product):
    "bronchitis, either tuberculosis or lung cancer B, D p(b,e)"
    ss = set(scope_product)
    if ss == set([("Bronchitis", True), ("EitherTL", True)]):
        return 1 / 90
    elif ss == set([("Bronchitis", False), ("EitherTL", True)]):
        return 1 / 11
    elif ss == set([("Bronchitis", True), ("EitherTL", False)]):
        return 1 / 39
    elif ss == set([("Bronchitis", False), ("EitherTL", False)]):
        return 1 / 5
    else:
        raise ValueError("Unknown scope product")


# instantiate factors with factor functions and implied random variables in scope
VisitAsia_cf = Factor(gid="VisitAsia_cf", scope_vars=set([VisitAsia]), factor_fn=phi_VisitAsia)
VisitAsiaTuberculosis_cf = Factor(
    gid="VisitAsiaTuberculosis_cf", scope_vars=set([VisitAsia, Tuberculosis]), 
    factor_fn=phi_TuberculosisVisitAsia
)
EitherTLXray_cf = Factor(
    gid="EitherTLXray_cf", scope_vars=set([EitherTL, Xray]), factor_fn=phi_EitherTLXray
)
Smoking_cf = Factor(gid="Smoking_cf", scope_vars=set([Smoking]), factor_fn=phi_Smoking)
SmokingBronchitis_cf = Factor(
    gid="SmokingBronchitis_cf", scope_vars=set([Smoking, Bronchitis]),
    factor_fn=phi_SmokingBronchitis
)
SmokingLungCancer_cf = Factor(
    gid="SmokingLungCancer_cf", scope_vars=set([Smoking, LungCancer]),
    factor_fn=phi_SmokingLungCancer
)
LungCancerEitherTLTuberculosis_cf = Factor(
    gid="LungCancerEitherTLTuberculosis_cf",
    scope_vars=set([EitherTL, LungCancer, Tuberculosis]), factor_fn=phi_LungCancerEitherTLTuberculosis
)

DysponeaCoughBronchitis_cf = Factor(
    gid="IHBronchitis_cf", scope_vars=set([Cough, Dysponea, Bronchitis]), factor_fn=phi_DysponeaCoughBronchitis
)

CoughBronchitisEitherTL_cf = Factor(
    gid="CoughBronchitisEitherTL_cf", scope_vars=set([Cough, EitherTL, Bronchitis]), 
    factor_fn=phi_CoughBronchitisEitherTL
)
BronchitisEitherTL_cf = Factor(
    gid="BronchitisEitherTL_cf", 
    scope_vars=set([EitherTL, Bronchitis]), 
    factor_fn=phi_BronchitisEitherTL
)


# instantiate lwf chain graph and make a query
cowell = LWFChainGraph(
    gid="cowell",
    nodes=set([Smoking, Bronchitis, LungCancer, EitherTL, VisitAsia, 
               Tuberculosis, Xray, Cough, Dysponea]),
    edges=set([SmokingBronchitis_c, SmokingLungCancer_c, 
               LungCancerEitherTL_c,
               VisitAsiaTuberculosis_c, TuberculosisEitherTL_c, 
               EitherTLXray_c, EitherTLCough_c, BronchitisCough_c,
               BronchitisDysponea_c, CoughDysponea_c]),
    factors=set([VisitAsia_cf, VisitAsiaTuberculosis_cf,
                 EitherTLXray_cf, Smoking_cf,
                 SmokingBronchitis_cf,
                 SmokingLungCancer_cf, 
                 LungCancerEitherTLTuberculosis_cf,
                 DysponeaCoughBronchitis_cf, CoughBronchitisEitherTL_cf, 
                 BronchitisEitherTL_cf])
)
evidences = set([("VisitAsia", True), ("Smoking", True), ("Xray", False)])

final_factor, a = cowell.cond_prod_by_variable_elimination(
    set([Bronchitis]), evidences
)

round(FactorOps.phi_normal(final_factor, set([("Bronchitis", True)])), 4)

# 0.60

\endcode
