"""
Unittests for baserandvar.py operations
"""

import math
import unittest

from pygmodels.randvar.randvartype.baserandvar import (
    BaseEvidence,
    BaseRandomVariable,
)
from pygmodels.value.codomain import CodomainValue
from pygmodels.value.domain import DomainValue


class BaseRandvarTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # dice random variable
        dicename = "dice"
        diceid = "dice01"
        dice_input_data = set([DomainValue(value=i, set_name=diceid) for i in range(1, 7)])

        def dice_f(x: DomainValue) -> CodomainValue:
            return CodomainValue(
                value=x.value,
                set_name="dice value",
                mapping_name="dice_f",
                domain_name=x.belongs_to,
            )

        def dice_distribution(x: CodomainValue):
            return x.value / 6.0

        #
        self.dice = BaseRandomVariable(
            randvar_id=diceid,
            randvar_name=dicename,
            data=None,
            input_data=dice_input_data,
            f=dice_f,
            marginal_distribution=dice_distribution,
        )

        def grade_f(x: DomainValue) -> CodomainValue:
            if x.value == "student_1":
                return CodomainValue(
                    value="F",
                    set_name="grades",
                    mapping_name="grade_f",
                    domain_name=x.belongs_to,
                )
            return CodomainValue(
                value="A",
                set_name="grades",
                mapping_name="grade_f",
                domain_name=x.belongs_to,
            )

        def grade_distribution(x: CodomainValue):
            return 0.1 if x.value == "F" else 0.9

        svar_dname = "student"
        svar_id = "student01"
        students = set(
            [
                DomainValue(value="student_1", set_name=svar_id),
                DomainValue(value="student_2", set_name=svar_id),
            ]
        )

        self.student_rvar = BaseRandomVariable(
            randvar_name=svar_dname,
            randvar_id=svar_id,
            input_data=students,
            data=None,
            f=grade_f,
            marginal_distribution=grade_distribution,
        )

        # base evidence tests
        self.grade_ev = BaseEvidence(
            evidence_id="grade-evidence",
            value=CodomainValue(
                value="F",
                set_name="grades",
                mapping_name="grade_f",
                domain_name=svar_id,
            ),
            randvar_id=self.student_rvar.id(),
            description="grade is observed to be F due to lack of ...",
            data=None,
        )

    def test_randvar_id(self):
        """"""
        self.assertEqual(self.dice.id(), "dice01")

    def test_evidence_id(self):
        """"""
        self.assertEqual(self.grade_ev.id(), "grade-evidence")

    def test_evidence_value(self):
        """"""
        self.assertEqual(
            self.grade_ev.value(),
            CodomainValue(
                value="F",
                set_name="grades",
                mapping_name="grade_f",
                domain_name="student01",
            ),
        )

    def test_evidence_belongs_to(self):
        """"""
        self.assertEqual(
            self.grade_ev.belongs_to(), self.student_rvar.id(),
        )

    def test_evidence_eq(self):
        """"""
        self.assertEqual(
            self.grade_ev,
            BaseEvidence(
                evidence_id="my other evidence",
                value=CodomainValue(
                    value="F",
                    set_name="grades",
                    mapping_name="grade_f",
                    domain_name="student01",
                ),
                randvar_id=self.student_rvar.id(),
                description=None,
                data=None,
            ),
        )

    def test_str(self):
        "test string representation"
        self.assertEqual(str(self.dice), "<RandomVariable :: id: dice01 name: dice>")

    def test_hash(self):
        "test hash function"
        self.assertEqual(
            hash(self.dice), hash("<RandomVariable :: id: dice01 name: dice>")
        )

    def test_image(self):
        """"""
        simage = frozenset([x.value for x in self.student_rvar.image()])
        compval = frozenset(["A", "F"])
        self.assertEqual(simage, compval)

    def test_inputs(self):
        """"""
        self.assertEqual(
            self.student_rvar.inputs,
            set(
                [
                    DomainValue(value="student_1", set_name="student01"),
                    DomainValue(value="student_2", set_name="student01"),
                ]
            ),
        )

    def test_p(self):
        """"""
        self.assertEqual(
            0.1,
            self.student_rvar.p(
                CodomainValue(
                    value="F",
                    set_name="grades",
                    mapping_name="grade_f",
                    domain_name="student01",
                )
            ),
        )
