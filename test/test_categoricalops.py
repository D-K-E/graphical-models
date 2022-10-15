"""!
\file test_categoricalops.py Contains tests for categoricalops.py
Categorical random variable operation tests
"""

import math
import unittest
from typing import Any, Optional
import pdb

from pygmodels.randvar.randvarmodel.categorical import (
    CatRandomVariable,
    NumCatRandomVariable,
)
from pygmodels.randvar.randvarops.numeric.boolops import BoolOps
from pygmodels.randvar.randvarops.numeric.numericops import NumericOps
from pygmodels.randvar.randvarops.categoricalops import NumericOps as CNumericOps
from pygmodels.randvar.randvartype.baserandvar import BaseEvidence
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
            [DomainValue(value=i, set_name=diceid) for i in range(1, 7)]
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
        self.dice = NumCatRandomVariable(
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
            is_type(
                x, originType=CodomainValue, shouldRaiseError=True, val_name="x",
            )
            return 0.7 if x.value == 0.1 else (1.0 - 0.7)

        # evidence
        self.intev = BaseEvidence(
            evidence_id="intelligence-evidence",
            value=CodomainValue(
                value=0.1,
                set_name="intelligence",
                mapping_name="intelligence_f",
                domain_name=svar_id,
            ),
            randvar_id=self.student_rvar.id(),
            description="intelligence evidence",
            data=None,
        )
        self.intelligence = CatRandomVariable(
            randvar_name="intelligence",
            randvar_id="intelligence_randvar",
            input_data=students,
            data={"evidence": self.intev},
            f=intelligence_f,
            marginal_distribution=intelligence_dist,
        )
        self.intelligence2 = NumCatRandomVariable(
            randvar_name="intelligence",
            randvar_id="intelligence_randvar",
            input_data=students,
            data={"evidence": self.intev},
            f=intelligence_f,
            marginal_distribution=intelligence_dist,
        )

        def grade_event(x: DomainValue) -> CodomainValue:
            """"""
            if x.value == "F":
                return CodomainValue(
                    value=0.2,
                    set_name="grade values",
                    mapping_name="grade_event",
                    domain_name=x.belongs_to,
                )
            elif x.value == "D":
                return CodomainValue(
                    value=0.4,
                    set_name="grade values",
                    mapping_name="grade_event",
                    domain_name=x.belongs_to,
                )
            elif x.value == "B":
                return CodomainValue(
                    value=0.6,
                    set_name="grade values",
                    mapping_name="grade_event",
                    domain_name=x.belongs_to,
                )
            else:
                raise ValueError("Unkown domain value " + str(x))

        def grade_dist(x: CodomainValue) -> float:
            if x.value == 0.2:
                return 0.25
            elif x.value == 0.4:
                return 0.37
            elif x.value == 0.6:
                return 0.38
            else:
                raise ValueError("unknown grade value: " + str(x))

        grades = set(
            [
                DomainValue(value="F", set_name="grade names"),
                DomainValue(value="D", set_name="grade names"),
                DomainValue(value="B", set_name="grade names"),
            ]
        )

        self.grade_ev = BaseEvidence(
            evidence_id="grade-evidence",
            value=CodomainValue(
                value=0.2,
                set_name="grade values",
                mapping_name="grade_event",
                domain_name="grade names",
            ),
            randvar_id="grade_rvar",
            description="grade evidence",
            data=None,
        )

        self.grade_rvar = CatRandomVariable(
            randvar_name="grade",
            randvar_id="grade_rvar",
            input_data=grades,
            data={"evidence": self.grade_ev},
            f=grade_event,
            marginal_distribution=grade_dist,
        )

    def test_max_marginal_value(self):
        self.assertEqual(
            NumericOps.max_marginal_value(self.intelligence, sampler=lambda x: x).value,
            0.1,
        )

    def test_max(self):
        self.assertEqual(
            NumericOps.max(self.intelligence, sampler=lambda x: x), 0.7,
        )

    def test_min(self):
        self.assertEqual(
            round(NumericOps.min(self.intelligence, sampler=lambda x: x), 3,), 0.3,
        )

    def test_min_marginal_value(self):
        """"""
        self.assertEqual(
            NumericOps.min_marginal_value(self.intelligence, sampler=lambda x: x).value,
            0.9,
        )

    def test_expected_value(self):
        """"""
        self.assertEqual(
            round(NumericOps.expected_value(self.dice, sampler=lambda x: x), 3,), 3.5,
        )

    def test_P_X_e(self):
        """"""
        self.assertEqual(
            round(NumericOps.P_X_e(self.intelligence), 4), 0.7,
        )

    def test_max_marginal_e(self):
        """ """
        self.assertEqual(
            round(NumericOps.max_marginal_e(self.student_rvar), 4,), 0.9,
        )

    def test_min_marginal_e(self):
        """"""
        self.assertEqual(
            round(NumericOps.min_marginal_e(self.student_rvar), 4,), 0.1,
        )

    def test_marginal_over(self):
        """"""
        margover = NumericOps.marginal_over(
            r=self.grade_rvar, other=self.dice, evidence=self.grade_ev
        )
        self.assertEqual(round(margover, 4), 3.5 * 0.25)

    def test_marginal_over_evidence_key(self):
        """"""
        margover = NumericOps.marginal_over_evidence_key(
            r=self.grade_rvar, other=self.dice
        )
        self.assertEqual(round(margover, 4), 3.5 * 0.25)

    def test_joint_without_evidence(self):
        """"""
        joint = NumericOps.joint(v=self.dice, r=self.dice)
        self.assertEqual(round(joint, 4), 3.5 * 3.5)

    def test_variance(self):
        """"""
        variance = NumericOps.variance(self.dice)
        self.assertEqual(round(variance, 3), 2.917)

    def test_standard_deviation(self):
        """"""
        sdev = NumericOps.standard_deviation(self.dice)
        self.assertEqual(round(sdev, 3), round(math.sqrt(2.917), 3))

    def test_p_x_fn(self):
        """"""

        def pfn(x: CodomainValue):
            if x.value == "F":
                return 0.0
            else:
                return 1.0

        #
        val = CNumericOps.p_x_fn(r=self.student_rvar, phi=pfn)
        self.assertEqual(val, 0.9)

    def test_expected_apply(self):
        """"""

        def pfn(x: CodomainValue):
            if x.value == "F":
                return 0.0
            else:
                return 1.0

        #
        val = CNumericOps.expected_apply(r=self.student_rvar, phi=pfn)
        self.assertEqual(val, 0.9)

    def test_apply_to_marginals(self):
        """"""

        def pfn(x):
            if x > 0.5:
                return 0.0
            else:
                return 1.0

        #
        val = CNumericOps.apply_to_marginals(r=self.student_rvar, phi=pfn)
        self.assertEqual(val, set([0.0, 1.0]))

    def test_reduce_to_value(self):
        ""
        red_val = CodomainValue(
            value=0.4,
            set_name="grade values",
            mapping_name="grade_event",
            domain_name="grade names",
        )
        nrand = CNumericOps.reduce_to_value(r=self.grade_rvar, val=red_val,)
        nimage = nrand.image()
        self.assertEqual(frozenset([red_val]), nimage)

    def test_max_joint(self):
        "maximum joint probability of two numeric categorical random variables"
        compval = round((1 / 6) * 0.7, 5)
        val = NumericOps.max_joint(r=self.intelligence2, v=self.dice)
        self.assertEqual(round(val, 5), compval)

    def test_conditional_1(self):
        "test conditional probability"
        # self.assertEqual(val, compval)
        val = NumericOps.conditional(other=self.intelligence2, r=self.dice)
        v1 = 0.7
        v2 = sum(1 / 6 * i for i in range(1, 7))
        compval = round(v2 * v1 / v1, 5)
        self.assertEqual(round(val, 5), compval)

    def test_conditional_2(self):
        "maximum joint probability of two numeric categorical random variables"
        # self.assertEqual(val, compval)
        val = NumericOps.conditional(r=self.intelligence2, other=self.dice)
        rv = sum(1 / 6 * i for i in range(1, 7))
        compval = round(rv * 0.7 / rv, 5)
        self.assertEqual(round(val, 5), compval)

    @unittest.skip("needs a reference value")
    def test_max_conditional(self):
        ""

    @unittest.skip("needs a reference value")
    def test_joint_matrix(self):
        ""


if __name__ == "__main__":
    unittest.main()
