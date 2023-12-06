"""
set operations based on types on value.py
"""

from pygmodels.value.valuetype.value import SetValue
from pygmodels.value.valuetype.value import NumericIntervalValue
from pygmodels.value.valuetype.value import R

from pygmodels.utils import is_type, is_all_type

from typing import Set, Generator, Iterator, Union, FrozenSet

from itertools import chain, combinations


class SetBoolOps:
    """"""

    @staticmethod
    def is_sigma_field(
        iterable: FrozenSet[Union[FrozenSet[SetValue], NumericIntervalValue]],
        sample_space: Union[FrozenSet[SetValue], R],
    ) -> bool:
        """
        \brief Check if iterable is sigma field on Space.

        see, LeGall, 2022, p. 4
        """
        is_all_type(iterable, "iterable", (frozenset, NumericIntervalValue), True)
        if not any(
            [
                is_all_type(
                    sample_space,
                    "sample_space",
                    (SetValue, NumericIntervalValue),
                    False,
                ),
                is_type(sample_space, "sample_space", NumericIntervalValue, False),
            ]
        ):
            raise TypeError(
                "sample_space must either be a numeric interval or a FrozenSet[SetValue]"
            )
        c1 = any(sample_space == a for a in iterable)
        c2 = all((sample_space - a) in iterable for a in iterable)
        c3 = True
        for subs in SetSetOps.mk_powerset(sample_space=iterable):
            if subs:
                ss = set(subs)
                s = ss.pop()
                for sub in ss:
                    s = s | sub
                c3 = c3 and any(s == i for i in iterable)

        return c1 and c2 and c3


class SetSetOps:
    """"""

    @staticmethod
    def mk_trivial_sigma_field(
        sample_space: Union[Set[Union[SetValue]], R]
    ) -> FrozenSet[Union[FrozenSet[SetValue], R]]:
        """
        Constructs a trivial sigma field from a given set E according to
        LeGall, 2022, p. 4
        """
        if isinstance(sample_space, (set, frozenset)):
            is_all_type(sample_space, "sample_space", SetValue, True)
            return frozenset([frozenset(), frozenset(sample_space)])
        elif isinstance(sample_space, R):
            return frozenset([frozenset(), sample_space])
        else:
            msg = "Only finite sets and R are supported as sigma fields"
            msg += f" argument has type {type(sample_space).__name__}"
            raise TypeError(msg)

    @staticmethod
    def mk_sigma_field_from_subset(
        sample_space: Union[FrozenSet[SetValue], R],
        subset: Union[
            FrozenSet[Union[SetValue, NumericIntervalValue]], NumericIntervalValue
        ],
    ):
        """
        From Venkatesh, 2013, p. 15
        """
        is_set = isinstance(sample_space, (set, frozenset))
        if is_set:
            is_all_type(sample_space, "sample_space", SetValue, True)
            is_all_type(subset, "subset", SetValue, True)
        else:
            is_type(sample_space, "sample_space", R, True)
            if isinstance(subset, (set, frozenset)):
                is_all_type(subset, "subset", NumericIntervalValue, True)
            else:
                is_type(subset, "subset", NumericIntervalValue, True)
        if not (subset <= sample_space):
            raise ValueError("given subset is not a subset of sample_space")
        sub_c = sample_space - subset
        return {
            frozenset(),
            frozenset(sample_space) if is_set else sample_space,
            subset,
            sub_c,
        }

    @staticmethod
    def add_subset_to_sigma_field(
        sample_space: Union[FrozenSet[SetValue], R],
        subset: FrozenSet[Union[SetValue, NumericIntervalValue]],
        field: FrozenSet[FrozenSet[Union[SetValue, NumericIntervalValue]]],
    ):
        """ """
        is_all_type(sample_space, "sample_space", SetValue, True)
        is_type(subset, "subset", frozenset, True)
        if not (subset <= sample_space):
            raise ValueError("given subset is not a subset of sample_space")
        sub_c = sample_space - subset
        field.add(subset)
        field.add(sub_c)
        return field

    @staticmethod
    def mk_sigma_field_from_subsets(
        sample_space: Union[FrozenSet[SetValue], R],
        subsets: FrozenSet[FrozenSet[SetValue]],
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
    def mk_powerset(sample_space: Set) -> Iterator[Set]:
        """
        Constructs the power set sigma field from a given set 'sample_space' according to
        LeGall, 2022, p. 4

        from: https://docs.python.org/3/library/itertools.html#itertools-recipes
        """
        return chain.from_iterable(
            combinations(sample_space, r) for r in range(len(sample_space) + 1)
        )
