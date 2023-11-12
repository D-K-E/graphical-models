"""
\brief event as defined in Biagini, Campanino, 2016, p. 5
"""

from pygmodels.randvar.randvartype.baserandvar import BaseRandomNumber
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.utils import mk_id
from typing import Optional


class DiscreteRandomNumber(BaseRandomNumber):
    """"""

    def __init__(self, *args, outcomes: Optional[PossibleOutcomes] = None, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        is_optional_type(outcomes, "outcomes", PossibleOutcomes, True)
        self._outcomes = outcomes

    @property
    def upper_bound(self) -> float:
        """"""
        if self._evidence is not None:
            return self._evidence.value().value
        f = max([out.value for out in self.outcomes])
        return f

    @property
    def lower_bound(self) -> float:
        """"""
        if self._evidence is not None:
            return self._evidence.value().value
        f = min([out.value for out in self.outcomes])
        return f

    @property
    def outcomes(self) -> PossibleOutcomes:
        """
        Biagini, Campanino, 2016, p. 5
        """
        if self._outcomes is None:
            raise ValueError("outcomes is none")
        return self._outcomes

    def __and__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"
        if not isinstance(other, Event):
            raise TypeError("other must be an event")
        #
        name = "(" + (", ".join([self.name, other.name])) + ")"
        if self._evidence is not None:
            outcomes = [self._evidence.value().fetch()]
        else:
            outcomes = [p.fetch() for p in self.outcomes]

        result = []
        for f in other.outcomes:
            for e in outcomes:
                e_prod_f = min([e.fetch(), f])
                rval = CodomainValue(
                    v=e_prod_f,
                    set_id=self.id(),
                    mapping_name="&",
                    domain_name=name,
                )
                result.append(rval)
        and_event = DiscreteRandomNumber(
            randvar_id=mk_id(), randvar_name=name, outcomes=result
        )
        return and_event

    def __or__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"
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
                ef_max = max([e, f.fetch()])
                rval = CodomainValue(
                    v=ef_max,
                    set_id=self.id(),
                    mapping_name="|",
                    domain_name=name,
                )
                result.append(rval)
        or_event = DiscreteRandomNumber(
            randvar_id=mk_id(), randvar_name=name, outcomes=PossibleOutcomes(result)
        )
        return or_event

    def __invert__(self) -> BaseRandomNumber:
        """
        Biagini, Campanino, 2016, p. 4
        """
        name = "~" + self.name
        if self._evidence is not None:
            c: CodomainValue = self._evidence.value()
            comp1 = 1 - c.fetch()
            new_outcomes = PossibleOutcomes(
                [
                    CodomainValue(
                        v=comp1,
                        set_id=self.id(),
                        mapping_name="~",
                        domain_name=self.name,
                    ),
                ]
            )
            return DiscreteRandomNumber(
                randvar_id=mk_id(), randvar_name=name, outcomes=new_outcomes
            )
        outs = []
        for out in self.outcomes:
            comp = 1 - out.fetch()
            cval = CodomainValue(
                v=comp,
                set_id=self.id(),
                mapping_name="~",
                domain_name=self.name,
            )
            outs.append(cval)
        new_outcomes = PossibleOutcomes(outs)
        return DiscreteRandomNumber(
            randvar_id=mk_id(), randvar_name=name, outcomes=new_outcomes
        )
