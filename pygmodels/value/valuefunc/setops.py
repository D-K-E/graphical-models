"""
set operations based on types on value.py
"""

from pygmodels.value.valuetype.value import SetValue
from pygmodels.value.valuetype.value import SubsetValue

from pygmodels.utils import is_type, is_all_type

from typing import Set, Generator, Iterator

from itertools import chain, combinations


class SetBoolOps:
    """"""

    @staticmethod
    def is_sigma_field(iterable: Set[SubsetValue], sample_space: Set[SetValue]) -> bool:
        """
        \brief Check if iterable is sigma field on Space.

        see, LeGall, 2022, p. 4
        """
        is_all_type(iterable, "iterable", SubsetValue, True)
        is_all_type(sample_space, "sample_space", SetValue, True)
        c1 = any(sample_space == a for a in iterable)
        c2 = all((sample_space - a) in iterable for a in iterable)
        N = len(iterable)
        fs = list(iterable)
        c3 = True
        for n in range(N):
            subs = fs[:n]
            if subs:
                r = subs.pop(0)
                for s in subs:
                    r += s
                #
                c3 = c3 and (r in iterable)
        #
        return c1 and c2 and c3


class SetSetOps:
    """"""

    @staticmethod
    def mk_trivial_sigma_field(sample_space: Set[SetValue]) -> Set[Set[SetValue]]:
        """
        Constructs a trivial sigma field from a given set E according to
        LeGall, 2022, p. 4
        """
        is_all_type(sample_space, "sample_space", SetValue, True)
        return {frozenset(), frozenset(sample_space)}

    @staticmethod
    def mk_sigma_field_from_subset(sample_space: Set[SetValue], subset: SubsetValue):
        """
        From Venkatesh, 2013, p. 15
        """
        is_all_type(sample_space, "sample_space", SetValue, True)
        is_type(subset, "subset", SubsetValue, True)
        if not (subset <= sample_space):
            raise ValueError("given subset is not a subset of sample_space")
        sub_c = sample_space - subset
        return {frozenset(), frozenset(sample_space), subset, sub_c}

    @staticmethod
    def add_subset_to_sigma_field(
        sample_space: Set[SetValue], subset: SubsetValue, field: Set[SubsetValue]
    ):
        """ """
        is_all_type(sample_space, "sample_space", SetValue, True)
        is_type(subset, "subset", SubsetValue, True)
        if not (subset <= sample_space):
            raise ValueError("given subset is not a subset of sample_space")
        sub_c = sample_space - subset
        field.add(subset)
        field.add(sub_c)
        return field

    @staticmethod
    def mk_sigma_field_from_subsets(
        sample_space: Set[SetValue], subsets: Set[SubsetValue]
    ):
        """
        From Shao, 2010, p. 2
        """
        field = SetSetOps.mk_trivial_sigma_field(sample_space)
        s = set()
        for subset in subsets:
            field = SetSetOps.add_subset_to_sigma_field(
                sample_space=sample_space, subset=subset, field=field
            )
            s |= subset
            s_c = sample_space - s
            field.add(frozenset(s))
            field.add(frozenset(s_c))
        return field

    @staticmethod
    def mk_powerset(sample_space: Set[SetValue]) -> Iterator[Set[SetValue]]:
        """
        Constructs the power set sigma field from a given set 'sample_space' according to
        LeGall, 2022, p. 4

        from: https://docs.python.org/3/library/itertools.html#itertools-recipes
        """
        return chain.from_iterable(
            combinations(sample_space, r) for r in range(len(sample_space) + 1)
        )