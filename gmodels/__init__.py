"""!
\mainpage 

# Graphical Models

[![Python package workflow ](https://github.com/D-K-E/graphical-models/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/D-K-E/graphical-models/actions/workflows/python-package.yml)


[![DOI](https://zenodo.org/badge/321839625.svg)](https://zenodo.org/badge/latestdoi/321839625)

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


## Guide for Contributors

As of now, most of the functions are unit tested. The test suit contains
around 170 tests covering most of the important functionality. However, there
can never be too much tests, so feel free to create a pull request with some
of your own.

Another area of improvement is documentation. As of now, we lack usage
examples for graph theoretical functionality of the library. Some functions
can also use more elaborate docstrings. Notice that we are not using sphinx or
other regular pythonic documentation generators. We are using
[doxygen](https://www.doxygen.nl/index.html). For the willing user, we provide
two templates for filling out docstrings in case she is not familiar with
doxygen way of doing things:

- Partial template:

\verbatim

def my_function(myarg1: str, myarg2: int) -> str:
    """!
    \brief One line explanation of functionality

    \param myarg1 description of the argument
    \param myarg2 description of the argument

    \return description of the returned value
    """
    return myarg1 + str(myarg2)

\endverbatim


- Full template:

\verbatim

def my_function(myarg1: str, myarg2: int) -> str:
    """!
    \brief One line explanation of functionality

    Long multilined
    description of
    functionality

    \param myarg1 description of the argument
    \param myarg2 description of the argument

    \exception TypeError description of the exception 

    \return description of the returned value

    \code{.py}

    >>> a = my_function("Lucky number is ", 7)
    >>> print(a)
    >>> "Lucky number is 7"

    \endcode

    """
    if isinstance(myarg2, int) is False:
        raise TypeError(
            "myarg2 " + str(myarg2) + " is of type " +
            str(type(myarg2))
            )
    return myarg1 + str(myarg2)

\endverbatim

Besides adding a documentation, you can also add other inference strategies.

Just file an issue in the case of doubt or signal your intent and we can
discuss the rest.

## Contributors

- [Nihan](https://github.com/comecloseridontbyte)


## Citation

This library has a mirror in another repository as well. The [Viva-Lambda
repository](https://github.com/Viva-Lambda/graphical-models) is in principal
identical to the
[D-K-E/graphical-models](https://github.com/D-K-E/graphical-models) (it might
be one or two commits behind). During the development of the library, the
weekly effort had been committed to that repository as well. However since the
DOI refers to D-K-E/graphical-models, it should be considered as the main
repository, and any references should refer to that one and not to
Viva-Lambda/graphical-models.

"""
