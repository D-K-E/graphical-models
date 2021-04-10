---
title: 'PyGModels: A Python package for exploring Probabilistic Graphical Models with Graph Theoretical Structures'
tags:
- Python
- probabilistic graphical models
- Bayesian statistics
- Probabilistic inference
authors:
- name: Doğu Kaan ERASLAN
  affiliation: 1
  orcid: 0000-0002-1552-8938
affiliations:
- name: EPHE, PSL
  index: 1
date: 02 February 2021
bibliography: paper.bib
---

# Summary

Probabilistic Graphical Models (PGMs) are a marriage between Graphs as in
Graph Theory, and Probability as in statistics and probability theory and are
widely used in many fields. We noticed that most existing PGM
libraries implement PGMs in a way that ignores their graphical nature.
`PyGModels`' value proposition is that it faithfully implements the graphical
nature of PGMs, thereby giving `PyGModels`' instantiated objects both
graph-theoretical and statistical properties, which allows users to explore
and test inference algorithms that are rooted in both graph theory or
statistics. `PyGModels` also implements several algorithms of interest on a
LWF chain graphs, also known as mixed graphs.

# Statement of Need

Though the students of computer science or statistics might find a pedagogical
value going through source code along with a textbook on probabilistic
graphical models (something like Sucar [see @Sucar_2015] or Cowell [see
@Cowell_2005] or Koller and Friedman [see @Koller_Friedman_2009]), we believe
that the value proposition of `PyGModels` speaks mostly to researchers.
Let us try to demonstrate the need for `PyGModels` by a use case. 

One has a set of categorical random variables in the form of a function
specified by a probability distribution. One has a set of edges that encode a
certain independence assumption over her random variables, and one has a set
of factors, that factorizes a certain probability distribution over her entire
graph. Given these, `PyGModels` might solve two major issues for the
researcher or the student alike:

1. Compute posterior probability distribution or most probable explanation
  given certain evidence.

2. Provide a basis for creating new algorithms of inference.

If the independence assumptions over the random variables requires the graph
to be a LWF chain graph where the graph can have both directed and undirected
edges, `PyGModels` can also solve:

3. Decomposing the chain graph into chain components

4. Moralizing the chain graph into a Markov Network.

5. Decomposing the chain graph into Conditional Random Fields.

Though the first issue is not irrelevant, the forte of `PyGModels` is the
second issue due to its lightweight nature and its direct embodiment of
statistical (we follow mostly Koller and Friedman [see @Koller_Friedman_2009]
for statistical conventions and definitions and inference algorithms) and
graph theoretic (we follow mostly Diestel [see @Diestel_2017] for graph
theoretic conventions and definitions; most of the graph algorithms come
from K. Erciyes [see @Erciyes_2018] and S. Even [see @Even_Guy_Even_2012];
exact pages are cited in doc strings of related functions inside the
source code) considerations in the same base class. 

The entire library depends only on python standard library which makes it very
extendible and easy to integrate and adapt to other projects as well. Through
its rigorous adoption of mathematical definitions of involved concepts, it
becomes feasible to extend arbitrary factors through their point wise product,
or apply common graph analysis algorithms such as finding articulation points
or bridges, or finding an optimal path defined by a cost function.

# Applications and Similar Works

PGMs are known for their wide range of applications in computer vision,
information retrieval, disease diagnosis and more recently, in the context of
our PhD thesis, annotations of ancient documents.

Other open sourced python libraries about PGMs include the following:

- `pyGM` [see @Ihler_2020]

- `pgmPy` [see @Indap_2013]

- `pgm` [see @Rauber_2019]

- `pgmpy` [see @Ankan_Panda_2015a]

- `pyfac` [see @Lester_2016]

- `pomegranate` [see @Schreiber_2018]

The most popular and goto libraries are `pgmpy` and `pomegranate`. Both of
them have also been used in several publications [see @Ankan_Panda_2015a; also
@Ankan_Panda_2015b; and @Schreiber_2018]. Their functionalities are covered
with nice test suites as well. Overall both of them are reliable libraries for
using PGMs in production.

`pyGM` and `pgm` are particularly well organized alternatives to `PyGModels`,
with `pyGM` being slightly more reliable than `pgm` due to its test suite.
`pyfac` seems to concerns itself only with inference over factor graphs and
`pgmPy` seems to be an inactive (last commit dates to 2013) side project
rather than a dedicated library. We will make a small comparison with `pgmpy`
most of our remarks hold for other alternatives as well.

`PyGModels` distinguishes from `pgmpy` by its lightweight nature (`PyGModels`
depends only on python 3.6 standard library). Our test suit cites its source
for most of the compared values inside doc string of functions for key
functions like inference over graphs. Factors are specified by a set of
random variables and a function whose domain is the cartesian product of
codomains of random variables. In all of the libraries above, a factor is
specified through an array of values. This has no direct implications on the
output. However, it has implications on the evaluation order of operations.
Our implementation is lazier and it conforms to the definition provided by
Koller and Friedman [see @Koller_Friedman_2009 p. 106-107]. The last aspect is
also the case for `pgmpy`, however `PyGModels` differs from it with respect to
the data structure used in the implementation.

The last aspect we deem important, is our capacity of doing inference on LWF
chain graphs (its theoretical foundations are best explained by S. Lauritzen
[see @Lauritzen_1996], the same author also provided its causal interpretation
in a long article clearing out misconceptions [see
@Lauritzen_Richardson_2002]; inference strategies over chain graphs are best
exposed by R. Cowell [see @Cowell_2005]; and more recently by R. Dechter [see
@Dechter_2019]), also known as mixed models or partially directed acyclic
graphs [see @Koller_Friedman_2009 p. 37]. Our library shows that once we have
the necessary set of factors, we can simply do inference over chain graphs
just as we do over other PGMs like Bayesian Networks and Markov Random Fields.
We implement several algorithms of interest for chain graphs such as
decomposition of chain graphs to chain components, moralization of chain
graphs.

# Acknowledgement

We acknowledge contributions from Nihan Özcan on her help with documentation
process. We also acknowledge AOROC Laboratory of EPHE, PSL University for
providing us the necessary tooling support during the development phase of
this library.

# References
