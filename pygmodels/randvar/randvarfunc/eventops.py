"""
\brief operations defined on event
"""
from pygmodels.randvar.randvarmodel.event import Event
from pygmodels.utils import is_type, is_all_type
from typing import List


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
        is_all_type(es, "es", Event, True)
        result = es.pop(0)
        for e in es:
            resut = result + e
        return all(outcome.value == 1 for outcome in result.outcomes)
