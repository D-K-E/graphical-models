"""!
\file test_categorical.py Tests of categorical.py objects
"""

import unittest

from pygmodels.randvar.randvarmodel.categorical import (
    CatRandomVariable,
    NumCatRandomVariable,
)
from pygmodels.randvar.randvartype.baserandvar import BaseEvidence
from pygmodels.utils import is_type, type_check
from pygmodels.value.codomain import CodomainValue
from pygmodels.value.domain import DomainValue


class CategoricalTest(unittest.TestCase):
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

    def test_marginal_with_known_value(self):
        """"""
        c1 = CodomainValue(value="F", set_name="grades", mapping_name="grade_f",)
        self.assertEqual(self.student_rvar.marginal(c1), 0.1)

    def test_p_x_known_value(self):
        """"""
        c1 = CodomainValue(value="F", set_name="grades", mapping_name="grade_f",)
        self.assertEqual(self.student_rvar.p(c1), 0.1)


if __name__ == "__main__":
    unittest.main()
