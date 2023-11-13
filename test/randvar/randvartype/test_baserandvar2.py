"""
\brief tests about baserandvar2.py
"""
import math
import unittest

from pygmodels.randvar.randvartype.baserandvar2 import (
    BaseEvidence,
    BaseRandomNumber,
)
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.domain import DomainValue
from pygmodels.value.valuetype.value import NumericValue


class BaseEvidenceTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # dice random variable
        svar_dname = "student"
        svar_id = "student01"

        self.student_rvar = BaseEvidence(
            evidence_id="student_1",
            randvar_id="student01",
            data=None,
            value=CodomainValue(
                set_id="student01",
                mapping_name="student_1_map",
                v=NumericValue(v=1),
            ),
        )

    def test_evidence_id(self):
        """"""
        self.assertEqual(self.student_rvar.id(), "student_1")

    def test_evidence_value(self):
        """"""
        self.assertEqual(
            self.student_rvar.value,
            CodomainValue(
                set_id="student01", mapping_name="student_1_map", v=NumericValue(v=1)
            ),
        )

    def test_evidence_belongs_to(self):
        """"""
        self.assertEqual(
            self.student_rvar.belongs_to,
            self.student_rvar.value.belongs_to,
        )

    def test_evidence_eq(self):
        """"""
        self.assertEqual(
            self.student_rvar,
            BaseEvidence(
                evidence_id="student_1",
                randvar_id="student01",
                data=None,
                value=CodomainValue(
                    set_id="student01",
                    mapping_name="student_1_map",
                    v=NumericValue(v=1),
                ),
            ),
        )

    def test_str(self):
        "test string representation"
        f = "<BaseEvidence :: id: student_1 value: <CodomainValue: 1 of set student01 mapped by student_1_map from None> belongs to: student01>"
        self.assertEqual(str(self.student_rvar), f)

    def test_hash(self):
        "test hash function"
        f = "<BaseEvidence :: id: student_1 value: <CodomainValue: 1 of set student01 mapped by student_1_map from None> belongs to: student01>"
        self.assertEqual(hash(self.student_rvar), hash(f))


if __name__ == "__main__":
    unittest.main()
