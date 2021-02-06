---
title: "PyGModels: A Python package for exploring Probabilistic Graphical
Models with Graph Theoretical Structures"

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
Fields again as a true digraph, and undirected graph, in the sense of graph
theory. In most cases, the input of our library is, a set of random variables
(functions specified by a certain probability distribution), edges that relate
these random variables to one another, and factors in the form of objects
which are instantiated by a set of random variables and a real valued
function. The library then provides several options for probabilistic
inference over these inputs, but more importantly since instantiated objects
have both graph theoretical and statistical properties, it provides a basis
for exploring ideas of inference algorithms that can both rooted in graph
theory or statistics.

# Statement of Need

Let us try to demonstrate the need for this library by a use case.

Though the name suggests otherwise PGMs and related software, for example

- [pyGM](https://github.com/ihler/pyGM)

- [pgmPy](https://github.com/indapa/pgmPy)

- [pgm](https://github.com/paulorauber/pgm)

are in most cases closer in nature to statistics than to graph theory. This
results in using specific structures like Factor Graphs, which do not
necessarily conform to the definition of a graph in the sense of Graph Theory.
The idea behind using these structures is that one has an established
inference scheme, and these structures simply make it easier to apply
inference algorithms. Our software takes the opposite approach. We privilege
graph theoretical structures and extend them to accommodate other structures
like factors.

Another important aspect of our library is its rigor in following mathematical
definitions where possible of the involved concepts. In most text books,
structures like factors and probability distributions are defined as but they
are parametrized as tables in most cases. We define both distributions and
factors as functions, and classes respectively. The factor is defined as a
class because several properties are more easily accessed that way. It is
still instantiated with a function that is defined over the set of values of
random variables in its domain.

Third and the last aspect we deem important, is the capacity of doing
inference on LWF chain graphs, also known as mixed models. Our library shows
that once we have the necessary set of factors, we can simply do inference
over chain graphs just as we do over other PGMs like Bayesian Networks and
Markov Random Fields. We implement several algorithms of interest for chain
graphs such as decomposition of chain graphs to chain components, moralization
of chain graphs.

# Acknowledgement

We acknowledge contributions from Nihan Özcan on her help with documentation
process. We also acknowledge CHart Laboratory of EPHE, PSL University
for providing us a laptop during the development phase of this library.
