import pytest
from typing import Union

from typing_exe.decorators import execute_annotations
from typing_exe.annotations import Assert, Modify, Sequence
from typing_exe.early_return import EarlyReturn


class TestAssert:
    def test_basic(self):
        @execute_annotations
        def fct(a: Assert[int, lambda a: a < 5]):
            return a

        assert fct(1) == 1

        with pytest.raises(ValueError):
            fct(5)

    def test_multiple(self):
        @execute_annotations
        def fct(
                a: Assert[lambda a: a != 0, lambda a: a % 3 == 0],
                b: int,
                c,
                d: Assert[int] = None
        ):
            return a, b, c, d

        assert fct(3, 1, 1) == (3, 1, 1, None)
        assert fct(6, b=1, c=1, d=1) == (6, 1, 1, 1)

        with pytest.raises(ValueError):
            fct(0, 1, 1, 1)

        with pytest.raises(ValueError):
            fct(1, 1, 1, 1)

    def test_typing(self):
        @execute_annotations
        def fct(a: Assert[Union[int, float], lambda a: a != 0]):
            return a

        assert fct(1) == 1

        with pytest.raises(ValueError):
            fct(0)

    def test_return(self):
        @execute_annotations
        def faulty_abs(a: int) -> Assert[lambda r: r >= 0]:
            return a

        assert faulty_abs(1) == 1

        with pytest.raises(ValueError):
            faulty_abs(-1)

    def test_args_without_typehints(self):
        @execute_annotations
        def div(a, b: Assert[lambda b: b != 0]):
            return a / b

        assert div(1, 1) == 1.

        with pytest.raises(ValueError):
            div(1, 0)

    def test_with_default_value(self):
        def none_to_one(parameter):
            if parameter is not None:
                assert type(parameter) is float

            parameter = 1. if parameter is None else parameter
            return parameter

        @execute_annotations
        def div(a, b: Modify[float, none_to_one] = None):
            return a / b

        assert div(2., 2.) == 1.
        assert div(2., None) == 2.
        assert div(2.) == 2.

        with pytest.raises(AssertionError):
            div(2., "not a float!")

    def test_with_star_args_fct(self):
        @execute_annotations
        def fct(a: Assert[lambda a: a != 0], *args):
            return a, *args

        assert fct(1, 2, 3, 4) == (1, 2, 3, 4)

        with pytest.raises(ValueError):
            fct(0, 1)

    def test_comparison_with_other_parameters(self):
        @execute_annotations
        def fct(a, b: Assert[lambda b, a: b > a] = 1):
            return a + b

        assert fct(1, 2) == 3
        assert fct(0) == 1

        with pytest.raises(ValueError):
            fct(1, 1)

    def test_comparison_with_other_parameters_false_names(self):
        @execute_annotations
        def fct(a, b: Assert[lambda b, notmyname: b > notmyname]):
            return a + b

        with pytest.raises(ValueError):
            fct(1, 2)


class TestModify:
    def test_basic(self):
        def hookfct(parameter):
            if parameter == 0:
                raise ValueError("Hook failed!")
            return (parameter + 1)**2

        @execute_annotations
        def fct(a: Modify[int, hookfct]) -> int:
            return a

        assert fct(1) == 4
        assert fct(2) == 9

        with pytest.raises(ValueError):
            fct(0)

    def test_returns(self):
        @execute_annotations
        def abs_fct(a: int) -> Modify[lambda a: abs(a)]:
            return a

        assert abs_fct(1) == 1
        assert abs_fct(-1) == 1

    def test_comparison_with_other_parameters(self):
        @execute_annotations
        def fct(a, b: Modify[lambda b, a: b + a]):
            return a, b

        assert fct(1, 1) == (1, 2)
        assert fct(a=3, b=1) == (3, 4)

    def test_comparison_with_other_parameters_false_names(self):
        @execute_annotations
        def fct(a, b: Modify[lambda b, notmyname: b + notmyname]):
            return a, b

        with pytest.raises(ValueError):
            fct(1, 2)


class TestSequence:
    def test_base(self):
        @execute_annotations
        def foo(
                a: Sequence[
                    int,
                    Assert[lambda a: a != 0],
                    Modify[lambda a: a + 1],
                    Assert[lambda a: a % 2 == 0]
                ]
        ):
            return a

        assert foo(1) == 2

        with pytest.raises(ValueError):
            foo(0)   # fails first check

        with pytest.raises(ValueError):
            foo(2)   # fails second check


class TestEarlyReturn:
    def test_base(self):
        def none_to_one(parameter):
            if parameter == 0.:
                return EarlyReturn(0.)   # just to check that the Check isn't triggered
            return parameter

        @execute_annotations
        def foo(
                a: Sequence[
                    Modify[none_to_one],
                    Assert[lambda a: a != 0]   # should never raise ValueError
                ]
        ):
            return a + 1.   # Just to make sure that this isn't triggered when EarlyReturn is used

        assert foo(1.) == 2.
        assert foo(0.) == 0.

    def test_in_different_positions(self):
        def hook1(p):
            if p == 0.:
                return EarlyReturn(0.)
            return p

        def hook2(p):
            if p == 2.:
                return EarlyReturn(4.)   # To see if calculation happens after function body
            return p

        @execute_annotations
        def foo(
                a: Modify[hook1] = EarlyReturn(-1.), /   # to test if it works positional only
        ) -> Modify[hook2]:
            return a + 1.

        assert foo() == -1.  # default EarlyReturn
        assert foo(0.) == 0.   # EarlyReturn from hook1
        assert foo(1.) == 4.   # EarlyReturn from hook2 (1. after hook1; 2. after fct body; 4. after hook2)
        assert foo(2.) == 3.   # regular function
