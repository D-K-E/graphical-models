"""
set operations based on types on value.py
"""

from pygmodels.value.valuetype.value import SetValue

from typing import Set, Generator

from itertools import chain, combinations


class SetBoolOps:
    """"""

    @staticmethod
    def is_sigma_field(A: Set[Set[SetValue]], E: Set[SetValue]):
        """
        \brief Check if A is sigma field on E.

        see, LeGall, 2022, p. 4
        """
        c1 = E in A
        c2 = all((E - a) in A for a in A)
        N = len(A)
        Alst = list(A)
        c3 = True
        for n in range(N):
            subs = Alst[:n]
            if subs:
                r = subs.pop(0)
                for s in subs:
                    r += s
                #
                c3 = c3 and (r in A)
        #
        return c1 and c2 and c3


class SetSetOps:
    """"""

    @staticmethod
    def mk_trivial_sigma_field(E: Set[SetValue]) -> Set[Set[SetValue]]:
        """
        Constructs a trivial sigma field from a given set E according to
        LeGall, 2022, p. 4
        """
        return {set(), E}

    @staticmethod
    def mk_powerset(E: Set[SetValue]) -> Generator[Set[SetValue]]:
        """
        Constructs the power set sigma field from a given set E according to
        LeGall, 2022, p. 4

        from: https://docs.python.org/3/library/itertools.html#itertools-recipes
        """
        return chain.from_iterable(combinations(E, r) for r in range(len(E) + 1))
