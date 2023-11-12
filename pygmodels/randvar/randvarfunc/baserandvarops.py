"""!
\file baserandvarops.py Base random variable operations. These operations are
defined for objects inheriting from \see BaseRandomVariable.
"""

from typing import Any, Callable, FrozenSet, List, Optional, Set, Tuple
from types import FunctionType, LambdaType
from uuid import uuid4

from pygmodels.randvar.randvartype.abstractrandvar import (
    AbstractEvidence,
    AbstractRandomVariable,
    PossibleOutcomes,
)
from pygmodels.randvar.randvartype.baserandvar import (
    BaseEvidence,
    BaseRandomVariable,
)
from pygmodels.utils import is_type
from pygmodels.value.codomain import CodomainValue, Outcome
from pygmodels.value.codomain import Range, RangeSubset
from pygmodels.value.value import NumericValue


class RandomVariableOps:
    """!
    Basic operations that can be applied to categorical random variables
    """

    @staticmethod
    def values(
        r: AbstractRandomVariable, sampler: Callable[[Range], RangeSubset]
    ) -> RangeSubset:
        """!
        \brief outcome values of the random variable

        \see CatRandomVariable constructor for more explanation about outcome
        values and their relation to random variables. \see
        CatRandomVariable. value_set for a more functional version of this
        function which let's you associate several transformations and filters
        before obtaining outcomes.

        \throws KeyError We raise a key error if there are no values associated
        to this random variable.

        \returns possible outcomes associated to this random variable.

        \code{.py}

        >>>
        >>> def grade_f(x: DomainValue) -> CodomainValue:
        >>>     if x.value == "student_1":
        >>>         return CodomainValue(
        >>>            value="F",
        >>>            set_name="grades",
        >>>            mapping_name="grade_f",
        >>>            domain_name=x.belongs_to,
        >>>         )
        >>>     return CodomainValue(
        >>>        value="A",
        >>>        set_name="grades",
        >>>        mapping_name="grade_f",
        >>>        domain_name=x.belongs_to,
        >>>     )
        >>>
        >>> def grade_distribution(x: CodomainValue):
        >>>     return 0.1 if x.value == "F" else 0.9

        >>> svar_dname = "student"
        >>> svar_id = "student01"
        >>> students = set([DomainValue(v="student_1", dom_id=svar_id),
        >>>                 DomainValue(v="student_2", dom_id=svar_id)])
        >>>
        >>> student_rvar = BaseRandomVariable(
        >>>     randvar_name=svar_dname,
        >>>     randvar_id=svar_id,
        >>>     input_data=students,
        >>>     data=None,
        >>>     f=grade_f,
        >>>     marginal_distribution=grade_distribution,
        >>> )
        >>> student_rvar.values()
        >>> frozenset(["A", "F"])

        \endcode
        """
        is_type(r, "r", AbstractRandomVariable, True)
        is_type(sampler, "sampler", FunctionType, True)
        return sampler(r.image())

    @staticmethod
    def value_set(
        r: AbstractRandomVariable,
        value_filter=lambda x: True,
        value_transform=lambda x: x,
        sampler=lambda x: x,
    ) -> FrozenSet[Tuple[str, CodomainValue]]:
        """!
        \brief the outcome value set of the random variable.

        \param value_filter function for filtering out values during the
        retrieval.

        \param value_transfom function for transforming values during the
        retrieval

        \returns codomain of random variable, that is possible outcomes
        associated to random variable

        This is basically the codomain of the function associated to random
        variable. Notice that this is completely different from probabilities
        and other statistical discussion.
        We also brand each value with the identifier of this random variable.
        When we are dealing with categorical random variables, this function
        should work, however for continuous codomains it would not really work.

        \code{.py}
        >>> students = PossibleOutcomes(frozenset(["student_1", "student_2"]))
        >>> grade_f = lambda x: "F" if x == "student_1" else "A"
        >>> grade_distribution = lambda x: 0.1 if x == "F" else 0.9
        >>> indata = {"possible-outcomes": students}
        >>> rvar = CatRandomVariable(
        >>>    input_data=indata,
        >>>    node_id="myrandomvar",
        >>>    f=grade_f,
        >>>    marginal_distribution=grade_distribution
        >>> )
        >>> rvar.value_set(
        >>>         value_transform=lambda x: x.lower(),
        >>>         value_filter=lambda x: x != "A"
        >>> )
        >>> frozenset([("myrandomvar","f")])

        \endcode
        """
        is_type(r, "r", AbstractRandomVariable, True)
        is_type(value_filter, "value_filter", LambdaType, True)
        is_type(value_transform, "value_transform", LambdaType, True)
        is_type(sampler, "sampler", LambdaType, True)
        sid = r.id()
        return frozenset(
            [
                (sid, value_transform(v))
                for v in RandomVariableOps.values(r, sampler)
                if value_filter(v) is True
            ]
        )

    @staticmethod
    def apply(
        r: AbstractRandomVariable,
        phi: Callable[[CodomainValue], Any],
        sampler=lambda x: x,
    ) -> FrozenSet[Any]:
        """!
        \brief apply function phi to possible outcomes of the random variable
        """
        is_type(phi, "phi", FunctionType, True)
        vs = RandomVariableOps.values(r, sampler=sampler)
        return frozenset([phi(v) for v in vs])

    @staticmethod
    def mk_new_randvar(
        r: AbstractRandomVariable, phi: Callable[[float], float]
    ) -> BaseRandomVariable:
        """!
        make a new random variable from given function with same distribution
        """
        rid = str(uuid4())
        is_type(phi, "phi", FunctionType, True)
        return BaseRandomVariable(
            randvar_id=rid,
            randvar_name="name: " + rid,
            f=phi,
            data=r.data(),
            input_data=r.inputs,
            marginal_distribution=r.dist,
        )

    @staticmethod
    def add_evidence(
        r: AbstractRandomVariable, evidence: AbstractEvidence
    ) -> AbstractRandomVariable:
        """!
        \brief add evidence to random variable

        \throws TypeError if the evidence is not a numeric value

        \todo Update documentation evidence has its own type now.

        \todo test DONE

        \code{.py}

        >>> nid1 = "rvar1"
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "noevidence": {"outcome-values": [0.1, 0.9]}
        >>> }

        >>> def intelligence_dist(intelligence_value: float) -> float:
        >>>    if intelligence_value == 0.1:
        >>>        return 0.7
        >>>    elif intelligence_value == 0.9:
        >>>        return 0.3
        >>>    else:
        >>>        return 0.0

        >>> # intelligence
        >>> noev = NumCatRVariable(
        >>>    node_id=nid1,
        >>>    input_data=input_data["noevidence"],
        >>>    marginal_distribution=intelligence_dist,
        >>> )
        >>> noev.add_evidence(0.9)
        >>> # now noev is same as intelligence

        \endcode
        """

        is_type(r, "r", AbstractRandomVariable, True)
        is_type(evidence, "evidence", AbstractEvidence, True)
        e = {"evidence": evidence}
        r.update_data(e)
        return r

    @staticmethod
    def pop_evidence(r: AbstractRandomVariable) -> AbstractRandomVariable:
        """!
        \brief remove evidence from this random variable

        \todo Update documentation evidence has its own type now.
        \todo test DONE

        \code{.py}

        >>> nid1 = "rvar1"
        >>> input_data = {
        >>>    "intelligence": {"outcome-values": [0.1, 0.9], "evidence": 0.9},
        >>>    "noevidence": {"outcome-values": [0.1, 0.9]}
        >>> }

        >>> def intelligence_dist(intelligence_value: float) -> float:
        >>>    if intelligence_value == 0.1:
        >>>        return 0.7
        >>>    elif intelligence_value == 0.9:
        >>>        return 0.3
        >>>    else:
        >>>        return 0.0

        >>> # intelligence
        >>> intelligence = NumCatRVariable(
        >>>    node_id=nid1,
        >>>    input_data=input_data["intelligence"],
        >>>    marginal_distribution=intelligence_dist,
        >>> )
        >>> intelligence.pop_evidence()
        >>> # now intelligence is same as noev

        \endcode
        """
        is_type(r, "r", AbstractRandomVariable, True)
        data = r.data()
        if "evidence" in data:
            data.pop("evidence")
        r.update_data(data)
        return r
