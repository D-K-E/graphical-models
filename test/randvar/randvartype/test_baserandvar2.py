"""
\brief tests about baserandvar2.py
"""
import math
import unittest

from pygmodels.randvar.randvartype.baserandvar2 import (
    BaseEvidence,
    BaseRandomNumber,
)
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcome
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.domain import DomainValue
from pygmodels.value.valuetype.value import NumericValue


class BaseEvidenceTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # dice random variable
        svar_dname = "student"
        self.svar_id = "student01"

        self.student_evidence = BaseEvidence(
            evidence_id="student_1",
            randvar_id=self.svar_id,
            data=None,
            value=PossibleOutcome(
                randvar_id=self.svar_id,
                v=NumericValue(v=1),
            ),
        )

    def test_evidence_id(self):
        """"""
        self.assertEqual(self.student_evidence.id, "student_1")

    def test_evidence_value(self):
        """"""
        self.assertEqual(
            self.student_evidence.value,
            PossibleOutcome(
                randvar_id=self.svar_id,
                v=NumericValue(v=1),
            ),
        )

    def test_evidence_belongs_to(self):
        """"""
        self.assertEqual(self.student_evidence.belongs_to, self.svar_id)

    def test_evidence_eq(self):
        """"""
        self.assertEqual(
            self.student_evidence,
            BaseEvidence(
                evidence_id="student_1",
                randvar_id=self.svar_id,
                data=None,
                value=PossibleOutcome(
                    randvar_id=self.svar_id,
                    v=NumericValue(v=1),
                ),
            ),
        )

    def test_str(self):
        "test string representation"
        f = '<BaseEvidence id="student_1" belongs_to="student01">\n'
        f += '  <CodomainValue set="NumericValue" mapped_by="student01">1</CodomainValue>\n'
        f += "</BaseEvidence>"
        self.assertEqual(str(self.student_evidence), f)

    def test_hash(self):
        "test hash function"
        f = '<BaseEvidence id="student_1" belongs_to="student01">\n'
        f += '  <CodomainValue set="NumericValue" mapped_by="student01">1</CodomainValue>\n'
        f += "</BaseEvidence>"
        self.assertEqual(hash(self.student_evidence), hash(f))


if __name__ == "__main__":
    unittest.main()
