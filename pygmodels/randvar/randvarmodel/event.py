"""
\brief event as defined in Biagini, Campanino, 2016, p. 5
"""

from pygmodels.randvar.randvartype.discrete import DiscreteRandomNumber
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.utils import mk_id


class Event(DiscreteRandomNumber):
    """"""

    def __init__(
        self,
        *args,
        outcomes: PossibleOutcomes = PossibleOutcomes(
            [
                CodomainValue(
                    v=NumericValue(v=0.0),
                    set_id=self.id(),
                    mapping_name=self.name,
                ),
                CodomainValue(
                    v=NumericValue(v=1.0),
                    set_id=self.id(),
                    mapping_name=self.name,
                ),
            ]
        ),
        **kwargs
    ):
        """"""
        super().__init__(*args, outcomes, **kwargs)
        if self._outcomes is not None:
            for out in self.outcomes:
                v = out.value
                if (v != 0) or (v != 1):
                    raise ValueError("an event may have 0 or 1 as possible outcome")

    def __or__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 5"
        if not isinstance(other, Event):
            raise TypeError("other must be an event")
        #
        name = "(" + (", ".join([other.name, self.name])) + ")"
        if self._evidence is not None:
            outcomes = [self._evidence.value().fetch()]
        else:
            outcomes = [p.fetch() for p in self.outcomes]

        result = []
        for f in other.outcomes:
            for e in outcomes:
                e_prod_f = e * f.fetch()
                e_plus_f = e + f.fetch()
                rval = CodomainValue(
                    v=e_plus_f - e_prod_f,
                    set_id=self.id(),
                    mapping_name="|",
                    domain_name=name,
                )
                result.append(rval)
        or_event = Event(
            randvar_id=mk_id(), randvar_name=name, outcomes=PossibleOutcomes(result)
        )
        return or_event
