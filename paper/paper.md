---
title: "PyGModels: A Python package for exploring Probabilistic Graphical Models oriented towards Graph Theory"

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

# Summary

Probabilistic Graphical Models (PGMs) are a marriage between Graphs as in
Graph Theory, and Probability as in statistics and probability theory. We aim
to concertize this conceptual marriage by using object oriented paradigms.
Most importantly, PGMs are a general framework which underlies most, if not
all of, the popular probabilistic structures, such as Hidden Markov Models, or
Bayesian Networks, that help with different artificial intelligence tasks. The
current implementation follows very closely the mathematical definitions of
all of the concepts involved in PGMs using several authoritative works as a
reference. The library is intended for testing research ideas that are
normally more easy to express using manual mathematical notation.

# Statement of Need

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
