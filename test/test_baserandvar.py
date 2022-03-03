"""
Unittests for baserandvar.py operations
"""

import math
import unittest

from pygmodels.randvar.randvartype.baserandvar import BaseRandomVariable
from pygmodels.value.codomain import CodomainValue
from pygmodels.value.domain import DomainValue


class BaseRandomVariableTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # dice random variable
        dicename = "dice"
        diceid = "dice01"
        dice_input_data = set(
            [DomainValue(v=i, dom_id=diceid) for i in range(1, 7)]
        )
        dice_f = lambda x: x
        dice_distribution = lambda x: x.v / 6.0
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
                DomainValue(v="student_1", dom_id=svar_id),
                DomainValue(v="student_2", dom_id=svar_id),
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

    def test_id(self):
        """"""
        self.assertEqual(self.dice.id(), "dice01")

    def test_str(self):
        "test string representation"
        self.assertEqual(
            str(self.dice), "<RandomVariable :: id: dice01 name: dice>"
        )

    def test_hash(self):
        "test hash function"
        self.assertEqual(
            hash(self.dice), hash("<RandomVariable :: id: dice01 name: dice>")
        )

    def test_image(self):
        """"""
        simage = frozenset(
            [x.value for x in self.student_rvar.image(sampler=lambda x: x)]
        )
        compval = frozenset(["A", "F"])
        self.assertEqual(simage, compval)

    def test_inputs(self):
        """"""
        self.assertEqual(
            self.student_rvar.inputs,
            set(
                [
                    DomainValue(v="student_1", dom_id="student01"),
                    DomainValue(v="student_2", dom_id="student01"),
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
