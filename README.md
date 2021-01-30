# Graphical Models

See the [documentation](https://viva-lambda.github.io/graphical-models/)

The library is focused on analysis than io. Everything is implemented from 
scratch. Only standard library is used for now. 
I might add numpy and cython later on if the performance becomes an issue 
(it most likely will ...). Very experimental stuff use it at your own risk.

The source code of this library aims to be accessible to all those interested
in Probabilistic Graphical Models. The primary goal is to facilitate the
understanding of models and basic inference strategies using well documented
data structures based only on Python 3 standard library. Functions are
annotated whenever possible.

Note that there are other alternatives on the subject:

- [pyGM](https://github.com/ihler/pyGM)

- [pgmPy](https://github.com/indapa/pgmPy)

- [pgm](https://github.com/paulorauber/pgm)

We distinguish from these by the following traits:

- Though not an entirely graph library like [NetworkX](https://networkx.org/),
  This library is more focused on Graph Theory than probabilistic structures.
  We implement several graph structures by the book. For example, `Tree`s are
  implemented as a `Graph`, just like `Path`s.

- Several graph analysis algorithms for:

    - Finding bridges

    - Finding articulation points

    - Finding connected components

    - Finding minimum and maximum spanning trees.
    
    - Finding shortest paths.

- We are also one of the rare open sourced python libraries that support
  inference on LWF Chain Graphs also known as [Mixed
  Graphs](https://en.wikipedia.org/wiki/Mixed_graph). As the overall library
  is not built for efficiency, we recommend not to use it in production. It
  should not be to difficult to transfer the concepts introduced in the source
  code though.

- References are important for us. Whenever possible we add a reference to a
  published ressource to the doc string of the function/class. This also
  applies for tests.

  

## Guide for Contributors

As of now, most of the functions are unit tested. The test suit contains
around 160 tests covering most of the important functionality. However, there
can never be too much tests, so feel free to PR some of your own.

Another area of improvement is documentation.

Adding other inference strategies are also welcome.

## Currently Supported Models

There are currently 4 primary models that might interest the general public:

### PGModel

`PGModel`, a graph with defined as `G=(V,E,F)` where `V` is vertex set
composed of `NumCatRVariable`s which are numeric categorical random variables,
`E` is edge set, and `F` is factor set.  
If `F` is none the factor set is deduced from edge set where each edge is
considered as a factor whose scope is the set of incident nodes to edge.
Sum-Product and Max-Product variable elimination are supported by `PGModel`.
Evidence encoded in nodes are directly used for reducing factors during the
instantiation of `PGModel`.
Additional evidence can be provided at query time as well for conditional and
mpe queries. `Marginal Map` queries are not yet supported.

Usage:
```python

from gmodels.pgmodel import PGModel
from gmodels.gtypes.edge import Edge, EdgeType
from gmodels.factor import Factor
from gmodels.randomvariable import NumCatRVariable

idata = {
            "a": {"outcome-values": [True, False]},
            "b": {"outcome-values": [True, False]},
            "c": {"outcome-values": [True, False]},
        }

a = NumCatRVariable(
            node_id="a", input_data=idata["a"], distribution=lambda x: 0.6 if x else 0.4
        )
b = NumCatRVariable(
    node_id="b", input_data=idata["b"], distribution=lambda x: 0.5 if x else 0.5
)
c = NumCatRVariable(
    node_id="c", input_data=idata["c"], distribution=lambda x: 0.5 if x else 0.5
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
queries = set([self.c])
product_factor, a = pgm.cond_prod_by_variable_elimination(queries, evidences)

print(round( product_factor.phi_normal(set([("c", True)])), 4))
# should give you 0.32

```


### Markov Network

Simply a `PGModel` whose edges are checked for being only undirected.

### Conditional Random Field

A markov network with target variables.


### LWF Chain Graphs

A `PGModel` with mixed edges.


## General Note

Most of the inference related functionality belongs to `PGModel` which largely
depend on methods defined in `Factor` class. Other models are treated as
different instances of `PGModel` whenever possible. This means that other
models are there to interface with different probability distributions.

## References

Here is a complete list of references used throughout the source code:
```bibtex

 @book{Cowell_2005, place={New York}, title={Probabilistic networks and expert systems}, url={http://accesbib.uqam.ca/cgi-bin/bduqam/transit.pl?&noMan=25126878}, publisher={Springer-Verlag}, author={Cowell, Robert G}, year={2005} }


 @article{Drton_2009, title={Discrete chain graph models}, volume={15}, ISSN={1350-7265}, url={http://arxiv.org/abs/0909.0843}, DOI={10.3150/08-BEJ172}, note={arXiv: 0909.0843}, number={3}, journal={Bernoulli}, author={Drton, Mathias}, year={2009}, month={Aug}, pages={736–753} }


 @book{Koller_Friedman_2009, place={Cambridge, MA}, series={Adaptive computation and machine learning}, title={Probabilistic graphical models: principles and techniques}, ISBN={978-0-262-01319-2}, publisher={MIT Press}, author={Koller, Daphne and Friedman, Nir}, year={2009}, collection={Adaptive computation and machine learning} }


 @book{Darwiche_2009, place={Cambridge ; New York}, title={Modeling and reasoning with Bayesian networks}, ISBN={978-0-521-88438-9}, publisher={Cambridge University Press}, author={Darwiche, Adnan}, year={2009} }

```

## Contributors

- [Nihan](https://github.com/comecloseridontbyte)

- [Kaan](https://github.com/D-K-E)
