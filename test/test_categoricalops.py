"""!
Categorical random variable operation tests
"""

import math
import unittest
from typing import Any, Optional

from pygmodels.randvar.randvarmodel.categorical import CatRandomVariable
from pygmodels.randvar.randvarops.categoricalops import (
    CatRandomVariableNumericOps,
    NumCatRandomVariableBoolOps,
    NumCatRandomVariableNumericOps,
    NumCatRandomVariableOps,
)
from pygmodels.utils import is_type, type_check
from pygmodels.value.codomain import CodomainValue
from pygmodels.value.domain import DomainValue


class CategoricalOpsTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # dice random variable
        dicename = "dice"
        diceid = "dice01"
        dice_input_data = set(
            [DomainValue(v=i, dom_id=diceid) for i in range(1, 7)]
        )

        def dice_f(x: DomainValue) -> CodomainValue:
            return CodomainValue(
                value=x.value,
                set_name=x.belongs_to,
                mapping_name="dice_f",
                domain_name=x.belongs_to,
            )

        def dice_distribution(x: CodomainValue):
            return 1.0 / 6.0

        #
        self.dice = CatRandomVariable(
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

        self.student_rvar = CatRandomVariable(
            randvar_name=svar_dname,
            randvar_id=svar_id,
            input_data=students,
            data=None,
            f=grade_f,
            marginal_distribution=grade_distribution,
        )

        # intelligence random variable
        def intelligence_f(x: DomainValue) -> CodomainValue:
            """"""
            if x.value == "student_1":
                return CodomainValue(
                    value=0.1,
                    set_name="intelligence",
                    mapping_name="intelligence_f",
                    domain_name=x.belongs_to,
                )
            return CodomainValue(
                value=0.9,
                set_name="intelligence",
                mapping_name="intelligence_f",
                domain_name=x.belongs_to,
            )

        def intelligence_dist(x: CodomainValue) -> float:
            """"""
            return 0.7 if x.value == 0.1 else (1.0 - 0.7)

        self.intelligence = CatRandomVariable(
            randvar_name="intelligence",
            randvar_id="intelligence_randvar",
            input_data=students,
            data={"evidence": 0.9},
            f=intelligence_f,
            marginal_distribution=intelligence_dist,
        )

    def test_max_marginal_value(self):
        self.assertEqual(
            NumCatRandomVariableNumericOps.max_marginal_value(
                self.intelligence, sampler=lambda x: x
            ).value,
            0.1,
        )

    def test_max(self):
        self.assertEqual(
            NumCatRandomVariableNumericOps.max(
                self.intelligence, sampler=lambda x: x
            ),
            0.7,
        )

    def test_min(self):
        self.assertEqual(
            round(
                NumCatRandomVariableNumericOps.min(
                    self.intelligence, sampler=lambda x: x
                ),
                3,
            ),
            0.3,
        )

    def test_min_marginal_value(self):
        """"""
        self.assertEqual(
            NumCatRandomVariableNumericOps.min_marginal_value(
                self.intelligence, sampler=lambda x: x
            ).value,
            0.9,
        )

    def test_expected_value(self):
        """"""
        self.assertEqual(
            round(
                NumCatRandomVariableNumericOps.expected_value(
                    self.dice, sampler=lambda x: x
                ),
                3,
            ),
            3.5,
        )

    def test_marginal_with_known_value(self):
        """"""
        c1 = CodomainValue(
            value="F",
            set_name="grades",
            mapping_name="grade_f",
        )
        self.assertEqual(self.student_rvar.marginal(c1), 0.1)

    def test_p_x_known_value(self):
        """"""
        c1 = CodomainValue(
            value="F",
            set_name="grades",
            mapping_name="grade_f",
        )
        self.assertEqual(self.student_rvar.marginal(c1), 0.1)

    @unittest.skip("not done")
    def test_P_X_e(self):
        """"""
        self.assertEqual(
            NumCatRandomVariableNumericOps.P_X_e(self.intelligence), 0.25
        )

    @unittest.skip("not done")
    def test_max_marginal_e(self):
        """"""
        self.assertEqual(self.grade.max_marginal_e(), 0.25)

    @unittest.skip("not done")
    def test_min_marginal_e(self):
        """"""
        self.assertEqual(self.grade.min_marginal_e(), 0.25)

    @unittest.skip("not done")
    def test_marginal_over(self):
        """"""
        eval_value = 0.2
        margover = self.grade.marginal_over(eval_value, self.dice)
        self.assertEqual(margover, 3.5 * 0.25)

    @unittest.skip("not done")
    def test_marginal_over_evidence_key(self):
        """"""
        margover = self.grade.marginal_over_evidence_key(self.dice)
        self.assertEqual(margover, 3.5 * 0.25)

    @unittest.skip("not done")
    def test_joint_without_evidence(self):
        dice = self.dice
        dice.pop_evidence()
        self.assertEqual(dice.joint(dice), 3.5 * 3.5)

    @unittest.skip("not done")
    def test_variance(self):
        self.assertEqual(round(self.dice.variance(), 3), 2.917)

    @unittest.skip("not done")
    def test_standard_deviation(self):
        """"""
        self.assertEqual(
            round(self.dice.standard_deviation(), 3),
            round(math.sqrt(2.917), 3),
        )
