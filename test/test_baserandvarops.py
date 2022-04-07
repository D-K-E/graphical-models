"""!
BaseRandomVariableOps tests
"""
import math
import unittest
from typing import Any, Optional

from pygmodels.randvar.randvarops.baserandvarops import RandomVariableOps
from pygmodels.randvar.randvartype.baserandvar import BaseRandomVariable
from pygmodels.utils import is_type, type_check
from pygmodels.value.codomain import CodomainValue
from pygmodels.value.domain import DomainValue


class RandomVariableOpsTest(unittest.TestCase):
    """"""

    def setUp(self):
        """"""
        # dice random variable
        dicename = "dice"
        diceid = "dice01"
        dice_input_data = set(
            [DomainValue(v=i, dom_id=diceid) for i in range(1, 7)]
        )

        def dice_f(x: DomainValue):
            return x

        def dice_distribution(x: DomainValue):
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

    def test_values(self):
        """"""
        simage = RandomVariableOps.values(
            self.student_rvar, sampler=lambda x: x
        )
        simage = frozenset([x.value for x in simage])
        compval = frozenset(["A", "F"])
        self.assertEqual(simage, compval)

    def test_value_set(self):
        """"""
        self.assertEqual(
            RandomVariableOps.value_set(
                r=self.student_rvar,
                value_transform=lambda x: x.value.lower(),
                value_filter=lambda x: x.value != "A",
                sampler=lambda x: x,
            ),
            frozenset([("student01", "f")]),
        )

    def test_apply(self):
        """"""

        def phi(x: CodomainValue) -> Any:
            "apply function to codomain"
            tval = is_type(
                val=x, originType=CodomainValue, shouldRaiseError=False
            )
            if tval:
                return x.value.lower() if x.value == "A" else x.value
            else:
                return 5.0

        #
        compval = frozenset(["a", "F"])
        vals = RandomVariableOps.apply(phi=phi, r=self.student_rvar)
        self.assertEqual(vals, compval)

    @unittest.skip("compare value not yet created")
    def test_mk_new_randvar(self):
        """"""
        pass
