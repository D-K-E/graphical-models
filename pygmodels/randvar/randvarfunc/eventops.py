"""
\brief operations defined on event
"""
from pygmodels.randvar.randvarmodel.event import Event
from pygmodels.utils import is_type, is_all_type
from typing import List, Tuple
from itertools import combinations


class EventBoolOps:
    """"""

    @staticmethod
    def is_incompatible(e: Event, f: Event) -> bool:
        "Biagini, Campanino, 2016, p. 6"
        is_type(e, "e", Event, True)
        is_type(f, "f", Event, True)
        #
        ef = e * f
        return all(outcome.value == 0 for outcome in ef.outcomes)

    @staticmethod
    def is_exhaustive(es: List[Event]):
        "Biagini, Campanino, 2016, p. 6"
        is_all_type(es, "es", Event, True)
        result = es.pop(0)
        for e in es:
            resut = result + e
        return all(outcome.value >= 1 for outcome in result.outcomes)

    @staticmethod
    def is_partition(es: List[Event]):
        "Biagini, Campanino, 2016, p. 6"
        exhaustive = EventBoolOps.is_exhaustive(es=es)
        return exhaustive and all(
            EventBoolOps.is_incompatible(e=ef[0], f=ef[1]) for ef in combinations(es, 2)
        )


class EventEventOps:
    """"""

    @staticmethod
    def partition_from_event(e: Event) -> Tuple[Event, Event]:
        """
        Make a partition from event following:
        Biagini, Campanino, 2016, p. 6
        """
        e_inv = ~e
        return (e, e_inv)
