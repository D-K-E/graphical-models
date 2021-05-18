# Graphical Models

[![Python package workflow ](https://github.com/D-K-E/graphical-models/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/D-K-E/graphical-models/actions/workflows/python-package.yml)


[![DOI](https://joss.theoj.org/papers/10.21105/joss.03115/status.svg)](https://doi.org/10.21105/joss.03115)


See doxygen generated [documentation](https://d-k-e.github.io/graphical-models/)


The source code of this library aims to be accessible to all those interested
in Probabilistic Graphical Models. The primary goal is to facilitate the
understanding of models and basic inference strategies using well documented
data structures based only on Python 3 standard library. Functions are
annotated whenever possible.

Note that there are other alternatives on the subject:

- [pyGM](https://github.com/ihler/pyGM)

- [pgmPy](https://github.com/indapa/pgmPy)

- [pgm](https://github.com/paulorauber/pgm)

- [pgmpy](https://github.com/pgmpy/pgmpy)

- [pomegranate](https://github.com/jmschrei/pomegranate)

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


## Installation

The entire library depends only on Python standard library. It is tested for
Python 3.6 through Github Actions at each push to the library. If you have
Python 3.6+, you should be good to go for installation.


If you want to install without creating a virtual environment, just go to the
main project directory that contains this readme file and call from terminal:

- `pip install .`


If you prefer conda for managing your virtual environments, simply create a
new environment:

- `conda create -n pygmodels python=3.6`

Activate the environment:

- `conda activate pygmodels`

Install the library:

- `pip install .`

Lastly test your installation with following command:

- `python -m unittest`

You should see something like the following on the terminal:

```python
Ran 179 tests in 0.666s

OK
```

## Usage Examples

See Related Pages section under the [docs](https://d-k-e.github.io/graphical-models/).

## Guide for Contributors

See [Contributing.md](CONTRIBUTING.md)

## Contributors

- [Nihan](https://github.com/comecloseridontbyte)


## Citation

For citing in a paper for general usage, use the JOSS paper DOI:
[![DOI](https://joss.theoj.org/papers/10.21105/joss.03115/status.svg)](https://doi.org/10.21105/joss.03115)


If you absolutely need to reference to a particular version of a source code,
you can use the zenodo DOI:

[![DOI](https://zenodo.org/badge/321839625.svg)](https://zenodo.org/badge/latestdoi/321839625)
