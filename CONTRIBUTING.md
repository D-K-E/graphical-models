First of all, thank you for your interest in contributing to this project.

# Guide for Contributors

There are three major areas of improvement besides fixing bugs:

- Unittests

- Documentation

- Code


## Unittests

The unittests are organized per file, so if we have `path.py`, 
we have `test_path.py` even if the `path.py` contains more than one class.
Having two classes in a single file is not the best design choice but it 
keeps the number of files in the project at a reasonable size. In any case,
if we create a new file for one of the classes contained in a file 
with multiple classes, the new file would get its corresponding test file as well.

As of now, most of the functions are unit tested. The test suit contains
around 180 tests covering most of the important functionality. However, there
can never be too much tests, so feel free to create a pull request with some
of your own.

## Documentation

Another area of improvement is documentation. As of now, we lack usage
examples for graph theoretical functionality of the library. Some functions
can also use more elaborate docstrings. Notice that we are not using sphinx or
other regular pythonic documentation generators. We are using
[doxygen](https://www.doxygen.nl/index.html). For the willing user, we provide
two templates for filling out docstrings in case she is not familiar with
doxygen way of doing things:

- Partial template:

```python

def my_function(myarg1: str, myarg2: int) -> str:
    """!
    \brief One line explanation of functionality

    \param myarg1 description of the argument
    \param myarg2 description of the argument

    \return description of the returned value
    """
    return myarg1 + str(myarg2)
```

- Full template:

```python

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
```

## Code and Functionality

Besides adding a documentation, you can also add other inference strategies or other graph algorithms.

There are two main criterias for contributing code:

- We do not plan to introduce any dependencies to the project, so only python 3 standard library is allowed.  

- Every function that you plan to add, no matter how tiny and trivial it might seem to you, must have an equivalent unittest.

**It is very important that each contributed functionality comes with its own set of unittests for each of its functions otherwise
it is going to be rejected**.

We deem the unittests as important as the added functionality.

## Other

Just file an issue in the case of doubt or signal your intent and we can
discuss the rest.
