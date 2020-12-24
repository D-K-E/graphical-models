# Graphical Models

The library is focused on analysis than io. Everything is implemented from 
scratch. Only standard library is used for now. 
I might add numpy and cython later on if the performance becomes an issue 
(it most likely will ...). Very experimental stuff use it at your own risk.

This library was first intended to be 

Bayesian statistics related bits and pieces all with basic libraries like
pandas and numpy, maybe some matplotlib here and there to help visualization.

- `BasicNaiveBayes.py` introduces concepts related to naive bayesian
  classification.

- `NaiveBayes.py` abstracts away some of the concepts introduced above.

Some simple distributions that depend on mean and standard deviation are
also implemented in bayesutils:

- gaussian distribution

- gumbel distribution

- laplace distribution

- logistic distribution
