"""!
\file test_categoricalops.py Contains tests for categoricalops.py
Categorical random variable operation tests
"""

import math
import unittest
from typing import Any, Optional

from pygmodels.randvar.randvarmodel.categorical import (
    CatRandomVariable,
    NumCatRandomVariable,
)
from pygmodels.randvar.randvarops.categoricalops import (
    CatRandomVariableNumericOps,
    NumCatRandomVariableBoolOps,
    NumCatRandomVariableNumericOps,
)
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
            is_type(
                x,
                originType=CodomainValue,
                shouldRaiseError=True,
                val_name="x",
            )
            return 0.7 if x.value == 0.1 else (1.0 - 0.7)

        # evidence
        self.intev = BaseEvidence(
            evidence_id="grade-evidence",
            value=CodomainValue(
                value="F",
                set_name="grades",
                mapping_name="grade_f",
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
                DomainValue(v="F", dom_id="grade names"),
                DomainValue(v="D", dom_id="grade names"),
                DomainValue(v="B", dom_id="grade names"),
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

    def test_P_X_e(self):
        """"""
        self.assertEqual(
            round(NumCatRandomVariableNumericOps.P_X_e(self.intelligence), 4),
            0.3,
        )

    def test_max_marginal_e(self):
        """ """
        self.assertEqual(
            round(
                NumCatRandomVariableNumericOps.max_marginal_e(
                    self.student_rvar
                ),
                4,
            ),
            0.9,
        )

    def test_min_marginal_e(self):
        """"""
        self.assertEqual(
            round(
                NumCatRandomVariableNumericOps.min_marginal_e(
                    self.student_rvar
                ),
                4,
            ),
            0.1,
        )

    def test_marginal_over(self):
        """"""
        margover = NumCatRandomVariableNumericOps.marginal_over(
            r=self.grade_rvar, other=self.dice, evidence=self.grade_ev
        )
        self.assertEqual(round(margover, 4), 3.5 * 0.25)

    def test_marginal_over_evidence_key(self):
        """"""
        margover = NumCatRandomVariableNumericOps.marginal_over_evidence_key(
            r=self.grade_rvar, other=self.dice
        )
        self.assertEqual(round(margover, 4), 3.5 * 0.25)

    def test_joint_without_evidence(self):
        """"""
        joint = NumCatRandomVariableNumericOps.joint(v=self.dice, r=self.dice)
        self.assertEqual(round(joint, 4), 3.5 * 3.5)

    def test_variance(self):
        """"""
        variance = NumCatRandomVariableNumericOps.variance(self.dice)
        self.assertEqual(round(variance, 3), 2.917)

    def test_standard_deviation(self):
        """"""
        sdev = NumCatRandomVariableNumericOps.standard_deviation(self.dice)
        self.assertEqual(round(sdev, 3), round(math.sqrt(2.917), 3))

    def test_p_x_fn(self):
        """"""

        def pfn(x: CodomainValue):
            if x.value == "F":
                return 0.0
            else:
                return 1.0

        #
        val = CatRandomVariableNumericOps.p_x_fn(r=self.student_rvar, phi=pfn)
        self.assertEqual(val, 0.9)

    def test_expected_apply(self):
        """"""

        def pfn(x: CodomainValue):
            if x.value == "F":
                return 0.0
            else:
                return 1.0

        #
        val = CatRandomVariableNumericOps.expected_apply(
            r=self.student_rvar, phi=pfn
        )
        self.assertEqual(val, 0.9)

    def test_apply_to_marginals(self):
        """"""

        def pfn(x):
            if x > 0.5:
                return 0.0
            else:
                return 1.0

        #
        val = CatRandomVariableNumericOps.apply_to_marginals(
            r=self.student_rvar, phi=pfn
        )
        self.assertEqual(val, set([0.0, 1.0]))


if __name__ == "__main__":
    unittest.main()
