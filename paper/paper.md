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
Graph Theory, and Probability as in statistics and probability theory. We aim
to concertize this conceptual marriage by using object oriented paradigms.
We designed the library for facilitating working with mathematical definitions
of the involved concepts. The goal is to facilitate testing inference
algorithms that depend graph theoretical structures in order to compute
probabilities in the case of PGMs. We do this by making the inferable
probabilistic graph, a true graph in the sense of graph theory. We also
implement other more specific PGMs like Bayesian Networks and Markov Random
Fields again as a true digraph, and undirected graph, respectively. In the
most common use cases, the input of our library is, a set of random variables
(functions specified by a certain probability distribution), edges that relate
these random variables to one another, and factors in the form of objects
which are instantiated by a set of random variables and a real valued
function. The library then provides several options for probabilistic
inference over these inputs, but more importantly since instantiated objects
have both graph theoretical and statistical properties, it provides a basis
for exploring ideas of inference algorithms that can both rooted in graph
theory or statistics.

# Statement of Need

Let us try to demonstrate the need for `PyGModels` by a use case. One has a
set of categorical random variables in the form of a function specified by a
probability distribution. One has a set of edges that encode a certain
independence assumption over her random variables, and one has a set of
factors, factorizes a certain probability distribution over her entire graph.
Given these, the API of `PyGModels` might solve two major issues for the
researcher or the student alike:

- Compute posterior probability distribution or most probable explanation
  given certain evidence.

- Test new algorithms of inference.

Though the first issue is not irrelevant, the forte of `PyGModels` is the
second issue due to its lightweight nature and its direct embodiment of
statistical and graph theoretic (we follow mostly Diestel [see @Diestel_2017]
for graph theoretic conventions and definitions; most of the graph algorithms
come from K. Erciyes [see @Erciyes_2018] and S. Even [see
@Even_Guy_Even_2012]; exact pages are cited in doc strings of related
functions inside the source code) considerations in the same base class.
The entire library depends only on python standard library which makes it
very extendible and easy to integrate and adapt to other projects as well.
Through its rigorous adoption of mathematical definitions of involved
concepts, it becomes feasible to extend arbitrary factors through their
point wise product, or apply common graph analysis algorithms such as
finding articulation points or bridges, or finding an optimal path defined
by a cost function.

# Applications and Similar Works

PGMs are known for their wide range of applications in computer vision,
information retrieval, disease diagnosis and more recently, in the context of
our phd thesis, annotations of ancient documents.

Other open sourced python libraries about PGMs include the following:

- `pyGM` [see @Ihler_2020]

- `pgmPy` [see @Indap_2013]

- `pgm` [see @Rauber_2019]

- `pgmpy` [see @Ankan_Panda_2015a]

- `pyfac` [see @Lester_2016]

The most popular and goto library is `pgmpy`. It has also been used in several
publications [see @Ankan_Panda_2015a; also @Ankan_Panda_2015b]. Its
functionality is covered with a nice test suite as well. Overall it is
reliable library for using PGMs in production. It comes with several
dependencies that can be heavy handed (`pytorch` for example) for exploratory
use though.

`pyGM` and `pgm` are particularly well organized alternatives to `PyGModels`,
with `pyGM` being slightly more reliable than `pgm` due to its test suite.
`pyfac` seems to concerns itself only with inference over factor graphs and
`pgmPy` seems to be an inactive (last commit is dates to 2013) side project
rather than a dedicated library. We will make a small comparison with `pgmpy`
most of our remarks hold for other alternatives as well.

`PyGModels` distinguish from `pgmpy` by its lightweight nature (`PyGModels`
depend only on python 3.6 standard library). Our test suit cites its source
for most of the compared values inside doc string of functions for key
functions like inference over graphs. Factors are specified by a set of
random variables and a function whose domain is the cartesian product of
codomains of random variables. In all of the libraries above, a factor is
specified through an array of values. Though it has not direct
implications on the output. It has implications on the evaluation order of
operations. Our implementation is lazier and it conforms to the
definition provided by Koller and Friedman [see @Koller_Friedman_2009 p.
106-107].


The last aspect we deem important, is our capacity of doing inference on LWF
chain graphs [for theoretical foundations see @Lauritzen_1996; its causal
interpretation is provided in @Lauritzen_Richardson_2002; for inference
strategies over chain graphs see @Cowell_2005; and more recently
@Dechter_2019], also known as mixed models or partially directed acyclic
graphs [see @Koller_Friedman_2009 p. 37]. Our library shows that once we
have the necessary set of factors, we can simply do inference over chain
graphs just as we do over other PGMs like Bayesian Networks and Markov Random
Fields. We implement several algorithms of interest for chain graphs such as
decomposition of chain graphs to chain components, moralization of chain
graphs.

# Acknowledgement

We acknowledge contributions from Nihan Özcan on her help with documentation
process. We also acknowledge CHart Laboratory of EPHE, PSL University for
providing us the necessary tooling support during the development phase of
this library.

# References
