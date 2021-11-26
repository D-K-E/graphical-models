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
- name: École Pratique des Hautes Études, Université PSL, Paris, France
  index: 1
date: 02 February 2021
bibliography: paper.bib
---

# Summary

Probabilistic Graphical Models (PGMs) are a marriage between "graphs" from
graph theory and "probability" from statistics and probability theory. While PGMs are
widely used in many fields, we noticed that most existing PGM
libraries are implement in a way that doesn't take full advantage of their graphical nature.
`PyGModels`' value proposition is that it faithfully implements the graphical
nature of PGMs, thereby giving `PyGModels`' instantiated objects both
graph-theoretical and statistical properties, which allows users to explore
and test inference algorithms that are rooted in graph theory or
statistics. `PyGModels` also implements several algorithms of interest on Lauritzen-Wermuth-Frydenberg
(LWF) chain graphs, also known as mixed graphs.

# Statement of Need

Though the students of computer science or statistics might find pedagogical
value going through source code along with a textbook on probabilistic
graphical models [for example @Cowell_2005; @Koller_Friedman_2009; @Sucar_2015],
`PyGModels` is mainly targeted at researchers.
Let us demonstrate the need for `PyGModels` with a use case.
Given a set of categorical random variables in the form of a function
specified by a probability distribution, a set of edges that encode a
certain independence assumption over these random variables, and a set
of factors that factorizes this probability distribution over the
graph, `PyGModels` is designed with the following use cases in mind:

1. computation of the posterior probability distribution or most probable explanation
  conditioned on evidence, and

2. the development of new inference algorithms.

The real forte of `PyGModels` is its support for implementing new algorithms
due to its lightweight nature and its direct implementation of
statistical and graph theoretic features in the same base class.
We mostly follow @Koller_Friedman_2009 for statistical conventions, definitions,
and inference algorithms. For graph theoretic conventions, we follow
@Diestel_2017, with algorithms from @Erciyes_2018 and @Even_Guy_Even_2012.
Throughout the code, exact pages for algorithmic references are cited in the
docstrings for relevant functions.

If the independence assumptions over the random variables requires the graph
to be a LWF chain graph where the graph can have both directed and undirected
edges, `PyGModels` can also (a) decompose the chain graph into chain components,
(b) moralize the chain graph into a Markov Network, and (c) decompose the chain
graph into Conditional Random Fields.

The entire library depends only on Python standard library which makes it easily
extensible, and straightforward to integrate or adapt to other projects. Through
its rigorous adoption of mathematical definitions of involved concepts, it
becomes feasible to extend arbitrary factors through their pointwise product,
or apply common graph analysis algorithms such as finding articulation points
or bridges, or finding an optimal path defined by a cost function.

# Applications and Similar Works

PGMs are known for their wide range of applications in computer vision,
information retrieval, disease diagnosis and more recently, in the context of
this author's PhD thesis, annotations of ancient documents.

Other open source Python libraries implementing PGMs include:

- `pyGM` [see @Ihler_2020]

- `pgmPy` [see @Indap_2013]

- `pgm` [see @Rauber_2019]

- `pgmpy` [see @Ankan_Panda_2015a]

- `pyfac` [see @Lester_2016]

- `pomegranate` [see @Schreiber_2018]

The most popular of these are `pgmpy` and `pomegranate`, both of
which have been used in several publications [see @Ankan_Panda_2015a;
@Ankan_Panda_2015b; @Schreiber_2018]. Their functionalities are covered
with nice test suites as well. Overall both of them are reliable libraries for
using PGMs in production.

`pyGM` and `pgm` are particularly well organized alternatives to `PyGModels`,
with `pyGM` being slightly more reliable than `pgm` due to its test suite.
`pyfac` is primarily focused on inference over factor graphs and
`pgmPy`'s development is inactive (last commit dates to 2013).
We will make a small comparison with `pgmpy`
most of our remarks hold for other alternatives as well.

`PyGModels` distinguishes from `pgmpy` by its lightweight nature (`PyGModels`
depends only on python 3.6 standard library). Our test suite cites its source
for most of the expected values in the function docstrings.
Factors are specified by a set of
random variables and a function whose domain is the Cartesian product of
codomains of random variables. In all of the libraries above, a factor is
specified through an array of values. This has no direct implications on the
output. However, it has implications on the evaluation order of operations.
Our implementation is lazier and it conforms to the definition provided by
Koller & Friedman [see @Koller_Friedman_2009 p. 106-107]. The last aspect is
also the case for other packages, however `PyGModels` differs from them with
respect to the data structure used in the implementation.

Another key feature, is `PyGModels`' support of inference on LWF
chain graphs. The theoretical foundations of these graphs are best explained by
@Lauritzen_1996, and its causal interpretation and common misconceptions are
discussed by @Lauritzen_Richardson_2002. Inference strategies over chain graphs are best
exposed by @Cowell_2005, and more recently by @Dechter_2019. These are also known
as mixed models or partially directed acyclic graphs [see @Koller_Friedman_2009 p. 37].
With `PyGModels`, once we have
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
