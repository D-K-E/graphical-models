"""!
\file baserandvar.py Base Random Variable object that implements the abstract
random variable interface. Inheriting from this object would make your object
usable for all the operations defined in \see baserandvarops.py.
"""

from typing import Callable, List, Optional, Set

from pygmodels.graph.graphtype.graphobj import GraphObject
from pygmodels.randvar.randvartype.abstractrandvar import (
    AbstractEvidence,
    AbstractRandomVariable,
    AssociatedValueSet,
)

# for type checking
from pygmodels.utils import is_type
from pygmodels.value.codomain import CodomainValue
from pygmodels.value.domain import Domain, DomainValue
from pygmodels.value.value import NumericValue


class BaseEvidence(AbstractEvidence, GraphObject):
    """!
    \brief A base class that implements the basic methods of the abstract evidence
    """

    def __init__(
        self,
        evidence_id: str,
        value: CodomainValue,
        randvar_id: str,
        description: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        """"""
        is_type(
            evidence_id, originType=str, shouldRaiseError=True, val_name="evidence_id",
        )
        is_type(
            randvar_id, originType=str, shouldRaiseError=True, val_name="randvar_id",
        )
        is_type(
            value, originType=CodomainValue, shouldRaiseError=True, val_name="value",
        )
        if description is not None:
            is_type(
                description,
                originType=str,
                shouldRaiseError=True,
                val_name="description",
            )
        if data is not None:
            is_type(
                data, originType=dict, shouldRaiseError=True, val_name="data",
            )
        # init graphobj
        super().__init__(oid=evidence_id, odata=data if data is not None else {})
        self.rand_id = randvar_id
        self.val = value
        self.descr = description

    def belongs_to(self) -> str:
        "Identifier of the random variable associated to evidence"
        return self.rand_id

    def value(self) -> CodomainValue:
        "Value of the evidence"
        return self.val

    def description(self) -> Optional[str]:
        "description of observation conditions of the evidence"
        return self.descr

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


class BaseRandomVariable(AbstractRandomVariable, GraphObject):
    """!
    \brief a Random Variable as defined by Koller, Friedman 2009, p. 20

    Citing from Koller, Friedman:
    <blockquote>
    Formally, a random variable, such as Grade, is defined by a function that
    associates with each outcome in \f$\Omega\f$ a value.
    </blockquote>

    It is important to note that domain and codomain of random variables are
    quite ambiguous. The \f$\Omega\f$ in the definition is set of possible
    outcomes, \see Domain object. In the context of probabilistic
    graphical models each random variable is also considered as a \see Node of
    a \see Graph. This object is meant to be a base class for further needs.
    It lacks quite a bit of methods. Hence it can not be used directly in a
    \see PGModel.

    """

    def __init__(
        self,
        randvar_id: str,
        randvar_name: Optional[str] = None,
        data: Optional[dict] = None,
        input_data: Optional[Domain] = None,
        f: Callable[[DomainValue], CodomainValue] = lambda x: x,
        marginal_distribution: Callable[[CodomainValue], float] = lambda x: 1.0,
    ):
        """!
        \brief Constructor for random variable

        \param marginal_distribution a function that takes in a value from
        codomain of the random variable and outputs a value in the range [0,1].
        Notice that is not a local distribution, it should be the marginal
        distribution that is independent of local structure.

        \param data The data associated to random variable can be anything
        \param randvar_id identifier of random variable. Same identifier is used
        as node identifier in a graph.
        \param randvar_name name of random variable for easy recognition
        \param f a function who takes data or from data, and outputs anything.

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
        super().__init__(oid=randvar_id, odata=data if data is not None else {})
        self.name = randvar_name
        if input_data is None and data is None:
            raise ValueError("Either input data or data must not be None")
        if input_data is None and data is not None:
            if "possible-outcomes" not in data:
                msg = "if input_data is not provided, provided data"
                msg += "must contain 'possible-outcomes' key"
                raise ValueError(msg)
            else:
                possible_outcomes = data["possible-outcomes"]
        elif input_data is not None:
            possible_outcomes = input_data
        else:
            raise ValueError("Unknown data configuration")
        self._inputs = possible_outcomes
        if not callable(f):
            raise TypeError("f must be a callable")
        self.f = f
        self._outs = None
        self.dist = marginal_distribution

    @property
    def inputs(self) -> Domain:
        """!"""
        return self._inputs

    def image(
        self, sampler: Callable[[Domain], List[DomainValue]]
    ) -> AssociatedValueSet:
        """!
        \brief Image of the random variable's function.

        There two ways of obtaining an image. We either specify a sampler at
        the constructor of RandomVariable or we specify it in this function. If
        both of the samplers are None during the calling of this method, we
        raise a TypeError. If both samplers are not None, we use the sampler
        provided during the function call and ignore the one provided in the
        constructor.

        \param sampler a function for sampling the domain of random variable if
        it is continuous or if it is too large.

        \returns either full range of the random variable or its subset
        depending on the sampler.

        \raises TypeError when both samplers are None, we raise type error.

        """
        if sampler is None:
            if self._outs is None:
                msg = "Sampler can not be none "
                msg += "if codomain values have not been assigned yet"
                raise ValueError(msg)
            return self._outs
        return frozenset(set(self.f(i) for i in sampler(self.inputs)))

    def p(self, outcome: CodomainValue) -> NumericValue:
        """!
        \brief probability of given outcome value as per the associated
        distribution

        \param value a member of \f$\Omega\f$ set of possible outcomes.

        \returns probability value associated to the outcome
        """
        return self.dist(outcome)

    def __eq__(self, other: AbstractRandomVariable) -> bool:
        """!
        Checks the instance first and then the probability distribution
        """
        if not isinstance(other, AbstractRandomVariable):
            return False
        if other.inputs != self.inputs:
            return False
        if other.image() != self.image():
            return False
        for ins in self.inputs:
            if other.p(ins) != self.p(ins):
                return False
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
