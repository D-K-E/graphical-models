from typing import Callable, List, Optional, Set, Tuple, Dict
from collections.abc import Iterable

from pygmodels.graph.graphtype.node import Node
from pygmodels.graph.graphtype.graphobj import GraphObject
from pygmodels.randvar.randvartype.abstractrandvar import (
    AbstractEvidence,
    AbstractEvent,
    AbstractRandomVariable,
    AbstractRandomNumber,
    AbstractRandomVariableMember,
)
from pygmodels.utils import is_type, is_optional_type
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcome
from types import FunctionType
from xml.etree import ElementTree as ET


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
        self._rand_id = randvar_id
        is_optional_type(description, "description", str, True)
        self._descr = description

    @property
    def belongs_to(self) -> str:
        "Identifier of the random variable associated to evidence"
        return self._rand_id

    @property
    def description(self) -> str:
        "description of observation conditions of the evidence"
        if self._descr is None:
            raise ValueError("descr is none")
        return self._descr


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
        description: Optional[str] = None,
    ):
        """"""
        super().__init__(
            member_id=evidence_id,
            randvar_id=randvar_id,
            data=data,
            description=description,
        )
        is_type(value, "value", PossibleOutcome, True)
        self._val = value

    @property
    def value(self) -> PossibleOutcome:
        "Value of the evidence"
        return self._val

    def __eq__(self, other: AbstractEvidence) -> bool:
        """!
        Checks the instance first and then the random variable identifiers and
        value.

        Note that the identifiers of evidence themselves do not play a role
        in their equality comparison
        """
        if not isinstance(other, AbstractEvidence):
            return False
        if other.value != self.value:
            return False
        if other.belongs_to != self.belongs_to:
            return False
        return True

    def __str__(self):
        """!
        String representation of an evidence
        """
        m = ET.Element("BaseEvidence")
        m.set("id", self.id)
        m.set("belongs_to", self.belongs_to)
        if self._descr is not None:
            m.set("description", self._descr)
        m.append(ET.fromstring(str(self.value)))
        return ET.tostring(m, encoding="unicode")

    def __hash__(self):
        """!
        \brief Obtain hash value from string representation of evidence
        """
        return hash(self.__str__())


class BaseRandomNumber(AbstractRandomNumber, Node):
    """"""

    def __init__(
        self,
        randvar_id: str,
        randvar_name: Optional[str] = None,
        data: Optional[dict] = None,
        evidence: Optional[BaseEvidence] = None,
    ):
        super().__init__(node_id=randvar_id, data=data)
        is_optional_type(evidence, "evidence", BaseEvidence, True)
        self._evidence = evidence
        is_optional_type(randvar_name, "randvar_name", str, True)
        self._name = randvar_name

    @property
    def name(self) -> str:
        """"""
        if self._name is None:
            raise ValueError("name is none")
        return self._name

    def __str__(self) -> str:
        """"""
        s = ET.Element("RandomNumber")
        s.set("id", self.id)
        if self._name is not None:
            s.set("name", self._name)
        if self._data is not None:
            d = ET.SubElement(s, "Data")
            for k, v in self.data.items():
                kd = ET.SubElement(d, str(k))
                kd.text = str(v)
        if self._evidence is not None:
            s.append(ET.fromstring(str(self.evidence)))
        return ET.tostring(s, encoding="unicode")
