"""!
\file factorops.py Operations on factors

The main objective of these functions is to operate on a given factor
or a set of factors.
"""

from typing import Set, Callable, Optional, List, Union, Tuple, FrozenSet
from pygmodels.pgmtype.factor import Factor, BaseFactor
from pygmodels.pgmtype.abstractpgm import AbstractFactor
from pygmodels.factorf.factoranalyzer import FactorAnalyzer
from pygmodels.pgmtype.randomvariable import NumCatRVariable, NumericValue

from itertools import product, combinations
from functools import reduce as freduce
from uuid import uuid4


class FactorOps:
    """!
    Analyzes a given factor
    """

    def __init__(self, f):
        ""
        if isinstance(f, AbstractFactor):
            fac = Factor.from_abstract_factor(f)
        elif isinstance(f, BaseFactor):
            fac = Factor.from_base_factor(f)
        elif isinstance(f, Factor):
            fac = f
        else:
            raise TypeError("argument must inherit from AbstractFactor object")
        self.factor = fac

    @classmethod
    def cls_product(
        cls,
        f: Factor,
        other: Factor,
        product_fn=lambda x, y: x * y,
        accumulator=lambda added, accumulated: added * accumulated,
    ) -> Tuple[Factor, float]:
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
        if not isinstance(f, Factor):
            raise TypeError("f argument needs to be a factor")

        if not isinstance(other, Factor):
            raise TypeError("other needs to be a factor")
        #
        svar = f.scope_vars()
        ovar = other.scope_vars()
        var_inter = svar.intersection(ovar)
        var_inter = list(var_inter)
        vsets = [v.value_set() for v in var_inter]
        inter_products = list(product(*vsets))
        smatch = f.factor_domain()
        omatch = other.factor_domain()
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
            ""
            for multip, match in common_match:
                if set(match) == set(scope_product):
                    return multip

        f = Factor(gid=str(uuid4()), scope_vars=svar.union(ovar), factor_fn=fx)
        return f, prod

    @classmethod
    def cls_reduced(
        cls, f: Factor, assignments: Set[Tuple[str, NumericValue]]
    ) -> Factor:
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
        return Factor(gid=str(uuid4()), scope_vars=svars, factor_fn=f.phi)

    @classmethod
    def cls_reduced_by_value(
        cls, f: Factor, assignments: Set[Tuple[str, NumericValue]]
    ):
        """!
        \brief \see Factor.reduced(context)

        \return Factor
        """
        return cls.cls_reduced(f, assignments)

    @classmethod
    def cls_filter_assignments(
        cls,
        f: Factor,
        assignments: Set[Tuple[str, NumericValue]],
        context: Set[NumCatRVariable],
    ) -> Set[Tuple[str, NumericValue]]:
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

    @classmethod
    def cls_reduced_by_vars(
        cls, f: Factor, assignments: Set[Tuple[str, NumericValue]],
    ):
        """!
        Koller, Friedman 2009, p. 111 follows the definition 4.5

        For \f$ U \not \subset Y \f$, we define \f$phi[u]\f$ to be
        \f$phi[U'=u']\f$, where \f$ U' = U \cap Y \f$ , and \f$u' = u<U>\f$,
        where \f$u<U>\f$ denotes the assignment in \f$u\f$ to the variables in
        \f$U'\f$.

        \return Factor
        """
        return cls.cls_reduced(f=f, assignments=assignments)

    @classmethod
    def cls_maxout_var(cls, f: Factor, Y: NumCatRVariable):
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
        if Y not in f:
            raise ValueError("argument is not in scope of this factor")

        Y_vals = Y.value_set()
        products = f.factor_domain()
        fn = f.factor_fn

        def psi(scope_product: Set[Tuple[str, NumericValue]]):
            ""
            s = set(scope_product)
            diffs = set([p for p in products if s.issubset(p) is True])
            return max([fn(d) for d in diffs])

        return Factor(
            gid=str(uuid4()), scope_vars=f.scope_vars().difference({Y}), factor_fn=psi,
        )

    @classmethod
    def cls_sumout_var(cls, f: Factor, Y: NumCatRVariable):
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
        if Y not in f:
            msg = "Argument " + str(Y)
            msg += " is not in scope of this factor: "
            msg += " ".join(f.scope_vars())
            raise ValueError(msg)

        Y_vals = Y.value_set()
        products = f.factor_domain()
        fn = f.factor_fn

        def psi(scope_product: Set[Tuple[str, NumericValue]]):
            ""
            s = set(scope_product)
            diffs = set([p for p in products if s.issubset(p) is True])
            return sum([fn(d) for d in diffs])

        return Factor(
            gid=str(uuid4()), scope_vars=f.scope_vars().difference({Y}), factor_fn=psi,
        )

    @classmethod
    def cls_sumout_vars(cls, f: Factor, Ys: Set[NumCatRVariable]):
        """!
        \brief Sum the variable out of factor as per Koller, Friedman 2009, p. 297

        \see Factor.sumout_var(Y)

        \return Factor
        """
        if len(Ys) == 0:
            raise ValueError("variables not be an empty set")
        if len(Ys) == 1:
            v = Ys.pop()
            return FactorOps.cls_sumout_var(f, v)
        ylst = list(Ys)
        fac = FactorOps.cls_sumout_var(f, ylst[0])
        for i in range(1, len(ylst)):
            fac = FactorOps.cls_sumout_var(fac, ylst[i])
        return fac

    def product(
        self,
        other: Factor,
        product_fn=lambda x, y: x * y,
        accumulator=lambda added, accumulated: added * accumulated,
    ) -> Tuple[Factor, float]:
        """!
        Wrapper of FactorOps.cls_product
        """
        return self.cls_product(
            f=self.factor, other=other, product_fn=product_fn, accumulator=accumulator
        )

    def reduced(self, assignments):
        """!
        Wrapper of FactorOps.cls_reduced
        """
        return self.cls_reduced(f=self.factor, assignments=assignments)

    def reduced_by_value(self, assignments):
        """!
        Wrapper of FactorOps.cls_reduced_by_value
        """
        return self.cls_reduced_by_value(f=self.factor, assignments=assignments)

    def filter_assignments(self, assignments):
        """!
        Wrapper of FactorOps.cls_filter_assignments
        """
        return self.cls_filter_assignments(f=self.factor, assignments=assignments)

    def reduced_by_vars(self, assignments):
        """!
        Wrapper of FactorOps.cls_reduced_by_vars
        """
        return self.cls_reduced_by_vars(f=self.factor, assignments=assignments)

    def maxout_var(self, Y: NumCatRVariable):
        """!
        Wrapper of FactorOps.cls_maxout_var
        """
        return self.cls_maxout_var(f=self.factor, Y=Y)

    def sumout_var(self, Y: NumCatRVariable):
        """!
        Wrapper of FactorOps.cls_sumout_var
        """
        return self.cls_sumout_var(f=self.factor, Y=Y)

    def sumout_vars(self, Ys: Set[NumCatRVariable]):
        """!
        Wrapper of FactorOps.cls_sumout_var
        """
        return self.cls_sumout_vars(f=self.factor, Y=Ys)
