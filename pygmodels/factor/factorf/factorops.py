"""!
\file factorops.py Operations on factors

The main objective of these functions is to operate on a given factor
or a set of factors.
"""

from functools import reduce as freduce
from itertools import combinations, product
from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pygmodels.factor.ftype.abstractfactor import (
    DomainSliceSet,
    DomainSubset,
    FactorCartesianProduct,
    FactorDomain,
    FactorScope,
)
from pygmodels.pgmtype.abstractpgm import AbstractFactor
from pygmodels.pgmtype.randomvariable import NumCatRVariable, NumericValue


class Factor2FactorableOps:
    """!
    Operations that give take a factor and give Tuple[FactorScope, Callable]

    The output is all that is required to make a factor, that is a set of
    random variables and a factor function.
    """

    @staticmethod
    def reduced(
        f: AbstractFactor, assignments: DomainSubset
    ) -> Tuple[FactorScope, Callable]:
        """!
        \brief reduce factor using given context

        \param assignments values that are assigned to random variables of this
        factor.

        \return Factor whose conditional probability table rows are shrink to
        rows that contain assignment values.

        Koller, Friedman 2009, p. 111 reduction by value example

        \f$phi(A,B,C)\f$

         A      B      C
        ---- | ---- | ----
         a1  |  b1  |  c1
         a1  |  b1  |  c2
         a2  |  b1  |  c1
         a2  |  b1  |  c2

        reduction C=c1 \f$\phi(A,B,C=c_1)\f$

           A      B      C
          ---- | ---- | ----
           a1  |  b1  |  c1
           a2  |  b1  |  c1

        """
        svars = set()
        for sv in f.scope_vars():
            for kval in assignments:
                k, value = kval
                if sv.id() == k:
                    sv.reduce_to_value(value)
            svars.add(sv)
        return tuple([svars, f.phi])

    @staticmethod
    def reduced_by_value(
        f: AbstractFactor, assignments: DomainSubset
    ) -> Tuple[FactorScope, Callable]:
        """!
        \brief \see Factor.reduced(context)

        \return a set of random variables and a factor function
        """
        return Factor2FactorableOps.reduced(f, assignments)

    @staticmethod
    def reduced_by_vars(
        f: AbstractFactor, assignments: DomainSubset
    ) -> Tuple[FactorScope, Callable]:
        """!
        Koller, Friedman 2009, p. 111 follows the definition 4.5

        For \f$ U \not \subset Y \f$, we define \f$phi[u]\f$ to be
        \f$phi[U'=u']\f$, where \f$ U' = U \cap Y \f$ , and \f$u' = u<U>\f$,
        where \f$u<U>\f$ denotes the assignment in \f$u\f$ to the variables in
        \f$U'\f$.

        \return Factor
        """
        return Factor2FactorableOps.reduced(f=f, assignments=assignments)

    @staticmethod
    def maxout_var(
        f: AbstractFactor, Y: NumCatRVariable
    ) -> Tuple[FactorScope, Callable]:
        """!
        \brief max the variable out of factor as per Koller, Friedman 2009, p. 555

        Maxing out a variable, or factor maximization is defined by Koller,
        Friedman as:
        <blockquote>
        Let X be a set of variables, and Y \f$ \not \in \f$ X, a random
        variable. Let \f$ \phi(X, Y) \f$ be a factor. We define the factor
        maximization of Y in \f$ \phi \f$ to be factor \f$ \psi \f$ over X such
        that: \f$ \psi(X) = max_{Y}\phi(X, Y) \f$
        </blockquote>

        \param Y random variable who is going to be maxed out.

        \throw ValueError If the argument is not in scope of this factor, we
        throw a value error

        \return Factor
        """
        if Y not in f.scope_vars():
            raise ValueError("argument is not in scope of this factor")

        # Y_vals = Y.value_set()
        products = FactorOps.cartesian(f)
        fn = f.phi

        def psi(scope_product: DomainSliceSet):
            """"""
            s = set(scope_product)
            diffs = set([p for p in products if s.issubset(p) is True])
            return max([fn(d) for d in diffs])

        return tuple([frozenset(f.scope_vars().difference({Y})), psi])

    @staticmethod
    def sumout_var(
        f: AbstractFactor, Y: NumCatRVariable
    ) -> Tuple[FactorScope, Callable]:
        """!
        \brief Sum the variable out of factor as per Koller, Friedman 2009, p. 297

        Summing out, or factor marginalization, is defined as the following by
        Koller, Friedman:

        <blockquote>

        Let X be a set of variables and Y \f$\not \in \f$ X a variable. Let
        \f$\phi(X, Y)\f] be a factor. We define the factor marginalization of Y
        in phi, denoted \f$ \sum_Y \phi \f$, to be a factor psi over X such
        that: \f$ \psi(X) = \sum_Y \phi(X,Y) \f$

        </blockquote>


        \param Y the variable that we are going to sum out.

        \throw ValueError We raise a value error if the argument is not in
        the scope of this factor

        \return Factor
        """
        if Y not in f.scope_vars():
            msg = "Argument " + str(Y)
            msg += " is not in scope of this factor: "
            msg += " ".join(f.scope_vars())
            raise ValueError(msg)

        # Y_vals = Y.value_set()
        products = FactorOps.cartesian(f)
        fn = f.phi

        def psi(scope_product: DomainSliceSet):
            """"""
            s = set(scope_product)
            diffs = set([p for p in products if s.issubset(p) is True])
            return sum([fn(d) for d in diffs])

        return tuple([frozenset(f.scope_vars().difference({Y})), psi])


class FactorOps:
    """!
    Operations a given factor
    """

    @staticmethod
    def product(
        f: AbstractFactor,
        other: AbstractFactor,
        product_fn=lambda x, y: x * y,
        accumulator=lambda added, accumulated: added * accumulated,
    ) -> Tuple[Tuple[FactorScope, Callable], float]:
        """!
        \brief Factor product operation from Koller, Friedman 2009, p. 107
        \f$ \psi(X,Y,Z) =  \phi(X,Y) \cdot \phi(Y,Z) \f$
        \f$ \prod_i phi(X_i) \f$

        Point wise product of two different factor functions.

        \param product_fn actual function for computing product. This function
        can be exchanged with another function to compute log-sum for example.

        \param accumulator this function decides how to accumulate resulting product.
        \param product_fn
        \parblock

        product function. Default case is that it multiplies
        its two arguments. In case of a floating precision problem it can be
        changed into summation.

        \endparblock

        \return tuple whose first element is the resulting factor and second
        element is the accumulated product.
        """
        if not isinstance(f, AbstractFactor):
            raise TypeError("f argument needs to be a factor")

        if not isinstance(other, AbstractFactor):
            raise TypeError("other needs to be a factor")
        #
        svar = f.scope_vars()
        ovar = other.scope_vars()
        var_inter = svar.intersection(ovar)
        var_inter = list(var_inter)
        vsets = [v.value_set() for v in var_inter]
        inter_products = list(product(*vsets))
        smatch = FactorOps.cartesian(f)
        omatch = FactorOps.cartesian(other)
        prod = 1.0
        common_match = set()
        for iproduct in inter_products:
            for o in omatch:
                for s in smatch:
                    ss = set(s)
                    ost = set(o)
                    prod_s = set(iproduct)
                    if prod_s.issubset(ss) and prod_s.issubset(ost):
                        common = ss.union(ost)
                        multi = product_fn(f.factor_fn(ss), other.factor_fn(ost))
                        common_match.add((multi, tuple(common)))
                        prod = accumulator(multi, prod)

        def fx(scope_product: Set[Tuple[str, NumericValue]]):
            """"""
            for multip, match in common_match:
                if set(match) == set(scope_product):
                    return multip

        f = tuple([frozenset(svar.union(ovar)), fx])
        return f, prod

    @staticmethod
    def filter_assignments(
        f: AbstractFactor, assignments: DomainSubset, context: FactorScope,
    ) -> DomainSubset:
        """!
        \brief filter out assignments that do not belong to context domain

        Scans the given set of assignements/evidences and removes those that do
        not belong to the context.

        \param context set of random variables that are relevant to current
        computation

        \param assignments evidences with respect to the value of a certain
        random variable in scope of the context.

        \return set of valid assignments
        """
        assignment_d = {a[0]: a[1] for a in assignments}
        context_ids = set([c.id() for c in context])
        for a in assignment_d.copy().keys():
            if a not in context_ids:
                assignment_d.pop(a)
        return set([(k, v) for k, v in assignment_d.items()])

    @staticmethod
    def factor_domain(
        f: AbstractFactor,
        D: Set[NumCatRVariable],
        rvar_filter: Callable[[NumCatRVariable], bool] = lambda x: True,
        value_filter: Callable[[NumericValue], bool] = lambda x: True,
        value_transform: Callable[[NumericValue], NumericValue] = lambda x: x,
    ) -> FactorDomain:
        """!
        \brief Get factor domain Val(D) D being a set of random variables

        \param D set of random variables
        \param rvar_filter filtering function for random variables
        \param value_filter filtering values from random variables' codomain
        \param value_transform apply a certain transformation to values from random variables' codomain.

        \return list of codomain of random variables

        \code

        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)

        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)

        >>> D = set([A,B])

        >>> fmatches = FactorOps.factor_domain(D=D)
        >>> print(fmatches)

        >>> [frozenset(("A", True), ("A", True)),
        >>>  frozenset(("B", True), ("B", False)),
        >>> ]

        \endcode

        """
        return [
            s.value_set(value_filter=value_filter, value_transform=value_transform)
            for s in D
            if rvar_filter(s)
        ]

    @staticmethod
    def phi_normal(f: AbstractFactor, scope_product: DomainSliceSet) -> float:
        """!
        \brief normalize a given factor value

        \param scope_product a row in conditional probability table of factor

        \return normalized value preference value

        \see Factor.normalize(phi_result), Factor.phi(scope_product)

        """
        Z = f.partition_value(FactorOps.factor_domain(f, D=f.scope_vars()))
        return f.phi(scope_product) / Z

    @staticmethod
    def cartesian(f: AbstractFactor) -> FactorCartesianProduct:
        """!
        \brief Compute cartesian product over factor domain

        The arguments are there for filtering or manipulating factor domain:
        \see FactorOps.factor_domain

        \code{.py}

        >>> A = NumCatRVariable("A",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)

        >>> B = NumCatRVariable("B",
        >>>                     input_data={"outcome-values": [True, False]},
        >>>                     marginal_distribution=lambda x: 0.5)

        >>> D = set([A,B])

        >>> fmatches = Factor.matches(D=D)
        >>> print(fmatches)

        >>> [frozenset([("A", True), ("B", True)]),
        >>>  frozenset([("A", True), ("B", False)]),
        >>>  frozenset([("A", False), ("B", True)]),
        >>>  frozenset([("A", False), ("B", False)])]

        \endcode
        """
        domain_values = FactorOps.factor_domain(f, D=f.scope_vars())
        return [frozenset(s) for s in list(product(*domain_values))]
