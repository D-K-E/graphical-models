"""!
\file baserandvar.py Base Random Variable object that implements the abstract
random variable interface. Inheriting from this object would make your object
usable for all the operations defined in \see baserandvarops.py.
"""

from typing import Callable, List, Optional, Set, Tuple, Dict
from collections.abc import Iterable

from pygmodels.graph.graphtype.node import Node
from pygmodels.randvar.randvartype.abstractrandvar import (
    AbstractEvidence,
    AbstractEvent,
    AbstractRandomVariable,
    AbstractRandomVariableMember,
    PossibleOutcome,
)

# for type checking
from pygmodels.utils import is_type, is_optional_type
from pygmodels.value.value import NumericValue
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcome
from types import FunctionType


class BaseRandomVariableMember(AbstractRandomVariableMember, GraphObject):
    """"""

    def __init__(
        self,
        member_id: str,
        randvar_id: str,
        description: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        """"""
        super().__init__(oid=member_id, odata=data)
        is_type(randvar_id, "randvar_id", str, True)
        self.rand_id = randvar_id
        is_optional_type(description, "description", str, True)
        self.descr = description

    def belongs_to(self) -> str:
        "Identifier of the random variable associated to evidence"
        return self.rand_id

    def description(self) -> Optional[str]:
        "description of observation conditions of the evidence"
        return self.descr


class BaseEvidence(AbstractEvidence, BaseRandomVariableMember):
    """!
    \brief A base class that implements the basic methods of the abstract evidence
    """

    def __init__(
        self,
        evidence_id: str,
        value: PossibleOutcome,
        randvar_id: str,
        data: Optional[dict] = None,
    ):
        """"""
        super().__init__(
            member_id=evidence_id,
            randvar_id=randvar_id,
            data=data,
            description=description,
        )
        is_type(value, "value", CodomainValue, True)
        self.val = value

    @property
    def value(self) -> PossibleOutcome:
        "Value of the evidence"
        return self.val

    def __eq__(self, other: AbstractEvidence) -> bool:
        """!
        Checks the instance first and then the random variable identifiers and
        value.

        Note that the identifiers of evidence themselves do not play a role
        in their equality comparison
        """
        if not isinstance(other, AbstractEvidence):
            return False
        if other.value() != self.value():
            return False
        if other.belongs_to() != self.belongs_to():
            return False
        return True

    def __str__(self):
        """!
        String representation of an evidence
        """
        msg = "<BaseEvidence :: id: "
        msg += self.id()
        msg += " value: " + str(self.value())
        msg += " belongs to: " + str(self.belongs_to())
        # this would create hash problems
        # msg += " description: " + (
        #    self.description() if self.description() is not None else ""
        # )
        msg += ">"
        return msg

    def __hash__(self):
        """!
        \brief Obtain hash value from string representation of evidence
        """
        return hash(self.__str__())


class BaseEvent(AbstractEvent, BaseRandomVariableMember):
    """!
    \brief A base class that implements the basic methods of the abstract event
    """

    def __init__(
        self,
        event_id: str,
        randvar_id: str,
        func: Callable[[Domain], PossibleOutcomes],
        data: Optional[dict] = None,
        description: Optional[str] = None,
    ):
        """"""
        super().__init__(
            member_id=event_id,
            randvar_id=randvar_id,
            data=data,
            description=description,
        )
        is_type(func, "func", FunctionType, True)
        self.f = func

    def __call__(self, sample: DomainValue) -> PossibleOutcome:
        """"""
        is_type(sample, "sample", DomainValue, True)
        return self.f(sample)


class RandomVariableInitializer:
    """!
    \brief It contains members for initializing a random variable
    """

    def __init__(
        self,
        event: BaseEvent,
        event_input: Optional[Domain] = None,
        input_sampler: Callable[[Domain], Iterable[DomainValue]] = lambda xs: frozenset(
            xs
        ),
        marginal_distribution: Optional[
            Callable[[CodomainValue], float]
        ] = lambda x: 1.0,
    ):
        """
        \param event_input domain of event
        \param event a measurable function which maps a domain to codomain
        \param input_sampler function that samples the \see event_input
        \param marginal_distribution a function that takes in a value from
        codomain of the random variable and outputs a value in the range [0,1].
        Notice that is not a local distribution, it should be the marginal
        distribution that is independent of local structure.

        """
        is_optional_type(event_input, "event_input", Domain, True)
        self.event_input = event_input
        is_optional(event, "event", BaseEvent, True)
        self.event = event
        is_optional(input_sampler, "input_sampler", FunctionType, True)
        self.input_sampler = input_sampler
        is_optional_type(event_sample_nb, "event_sample_nb", int, True)
        self.arg_dist = marginal_distribution
        self.distribution = self.init()

    def init(self):
        """check if initialization is possible"""
        if any(
            [
                a is None
                for a in [
                    self.event_input,
                    self.event,
                    self.input_sampler,
                    self.nb_samples,
                ]
            ]
        ) or (self.arg_dist is None):
            msg = "Either [event_input, event, event_sample_nb, input_sampler]"
            msg += " or marginal_distribution must be provided to initialize"
            msg += " random variable"
            raise ValueError(msg)
        if self.arg_dist is None:
            out_count = {}
            sample_count = 0
            for input_sample in self.input_sampler(self.event_input):
                output = self.event(input_sample)
                if output not in out_count:
                    out_count[output] = 0
                out_count[output] += 1
                sample_count += 1
            #
            def dist_fn(out: CodomainValue):
                value = out_count[out] / sample_count
                return value

            return dist_fn
        else:
            return self.arg_dist


class BaseRandomVariable(AbstractRandomVariable, GraphObject):
    """!
    \brief a Random Variable as defined by Koller, Friedman 2009, p. 20

    Citing from Koller, Friedman:
    <blockquote>
    Formally, a random variable, such as Grade, is defined by a function that
    associates with each outcome in \f$\Omega\f$ a value.
    </blockquote>
    """

    def __init__(
        self,
        randvar_id: str,
        initializer: Optional[RandomVariableInitializer] = None,
        randvar_name: Optional[str] = None,
        graph_data: Optional[dict] = None,
        evidence: Optional[BaseEvidence] = None,
    ):
        """!
        \brief Constructor for random variable


        \param data The data associated to random variable can be anything
        \param randvar_id identifier of random variable. Same identifier is used
        as node identifier in a graph.
        \param randvar_name name of random variable for easy recognition
        \param initializer controls random variable initialization. A random
        variable can be initialized either by passing its marginal distribution
        or passing an event and its related objects \see RandomVariableInitializer

        \returns a random variable instance

        \throws ValueError We raise a value error if the probability values
        associated to outcomes add up to a value bigger than one.

        For other parameters and the definition of a random variable \see
        RandomVariable.

        A simple data specification is provided for passing evidences and
        input. The possible outcomes key holds a set of values belonging to
        space of possible outcomes. If the input data just contains a key as
        'possible-outcomes', we suppose that it contains a object which
        represents the space of all possible outcomes of the measurable event
        set associated to random variable.

        The function associated to our random variable transforms the set of
        possible outcomes to values as per its definition in Koller, Friedman,
        2009, p. 20. Lastly we check whether obtained, or associated
        outcome-values satisfy the probability rule by checking if the
        probabilities associated to these values add up to one.

        \code{.py}

        >>>
        >>> dicename = "dice"
        >>> diceid = "dice01"
        >>> dice_input_data = set(
        >>>    [DomainValue(v=i, dom_id=diceid) for i in range(1, 7)]
        >>> )
        >>> dice_f = lambda x: x
        >>> dice_distribution = lambda x: x.v / 6.0
        >>> dice = BaseRandomVariable(
        >>>    randvar_id=diceid,
        >>>    randvar_name=dicename,
        >>>    data=None,
        >>>    input_data=dice_input_data,
        >>>    f=dice_f,
        >>>    marginal_distribution=dice_distribution,
        >>> )
        >>>

        \endcode

        constructor for a random variable"""
        super().__init__(oid=randvar_id, odata=graph_data)
        # check type errors
        is_optional_type(randvar_name, "randvar_name", str, True)
        self.name = randvar_name
        is_optional_type(evidence, "evidence", BaseEvidence, True)
        self.evidence = evidence
        if evidence is None and graph_data is not None:
            if "evidence" in graph_data:
                is_type(graph_data["evidence"], "evidence", BaseEvidence, True)
                self.evidence = graph_data["evidence"]
        #
        is_optional_type(initializer, "initializer", RandomVariableInitializer, True)
        if (graph_data is None) and (initializer is None):
            msg = "either the initializer or the graph_data with"
            msg += " enough information to instantiate the initializer must be"
            msg += " provided"
            raise ValueError(msg)
        if initializer is None:
            event_keys = ["event_input", "event", "input_sampler"]
            marginal_dist_key = "marginal_distribution"
            in_gdata = all(e for e in graph_data)
            in_m_gdata = marginal_dist_key in graph_data
            if (not in_gdata) and (not in_m_gdata):
                msg = f"Either {event_keys} or {marginal_dist_key}"
                msg += " must be present in graph_data"
                raise ValueError(msg)
            initializer = RandomVariableInitializer(
                event_input=graph_data["event_input"],
                event=graph_data["event"],
                input_sampler=graph_data["input_sampler"],
                marginal_distribution=graph_data["marginal_distribution"],
            )
            self.dist = initializer.distribution
            self.event = initializer.event
        else:
            self.dist = initializer.distribution
            self.event = initializer.event

    def __call__(self, outcome: CodomainValue) -> float:
        """!
        \brief probability of given outcome value as per the associated
        distribution

        \param value a member of \f$\Omega\f$ set of possible outcomes.

        \returns probability value associated to the outcome
        """
        is_type(outcome, "outcome", CodomainValue, True)
        return self.dist(outcome)

    def marginal(self, outcome: CodomainValue) -> float:
        """!
        \brief marginal distribution that is the probability of an outcome

        from Biagini, Campanino, 2016, p. 35
        <blockquote>
        Marginal distribution of X is the function: \f$p_1(x_i) = P(X=x_i)\f$
        </blockquote>

        \see CatRandomVariable.p

        \returns probability value associated to value

        \todo test DONE
        """
        return self(outcome)

    def __eq__(self, other: AbstractRandomVariable) -> bool:
        """!
        Checks the instance first and then the probability distribution
        """
        if not isinstance(other, AbstractRandomVariable):
            return False
        if other.event.id() != self.event.id():
            return False
        # for ins in self._sampler(self.inputs):
        #    if other.p(ins) != self.p(ins):
        #        return False
        return True

    def __str__(self):
        """!
        String representation of a random variable
        """
        msg = "<RandomVariable :: id: "
        msg += self.id()
        msg += " name: " + (self.name if self.name is not None else "None")
        msg += ">"
        return msg

    def __hash__(self):
        """!
        \brief Obtain hash value from string representation of RandomVariable
        """
        return hash(self.__str__())
