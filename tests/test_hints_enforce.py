import pytest
import typing_exe as texe
from typing import Union


class TestChecks:
    def test_basic(self):
        @texe.decorators.enforce
        def fct(a: texe.annotations.Checks[int, lambda a: a < 5]):
            return a

        assert fct(1) == 1

        with pytest.raises(ValueError):
            fct(5)

    def test_multiple(self):
        @texe.decorators.enforce
        def fct(
                a: texe.annotations.Checks[lambda a: a != 0, lambda a: a % 3 == 0],
                b: int,
                c,
                d: texe.annotations.Checks[int] = None
        ):
            return a, b, c, d

        assert fct(3, 1, 1) == (3, 1, 1, None)
        assert fct(6, b=1, c=1, d=1) == (6, 1, 1, 1)

        with pytest.raises(ValueError):
            fct(0, 1, 1, 1)

        with pytest.raises(ValueError):
            fct(1, 1, 1, 1)

    def test_typing(self):
        @texe.decorators.enforce
        def fct(a: texe.annotations.Checks[Union[int, float], lambda a: a != 0]):
            return a

        assert fct(1) == 1

        with pytest.raises(ValueError):
            fct(0)

    def test_return(self):
        @texe.decorators.enforce
        def faulty_abs(a: int) -> texe.annotations.Checks[lambda r: r >= 0]:
            return a

        assert faulty_abs(1) == 1

        with pytest.raises(ValueError):
            faulty_abs(-1)

    def test_args_without_typehints(self):
        @texe.decorators.enforce
        def div(a, b: texe.annotations.Checks[lambda b: b != 0]):
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

        @texe.decorators.enforce
        def div(a, b: texe.annotations.Hooks[float, none_to_one] = None):
            return a / b

        assert div(2., 2.) == 1.
        assert div(2., None) == 2.
        assert div(2.) == 2.

        with pytest.raises(AssertionError):
            div(2., "not a float!")

    def test_with_star_args_fct(self):
        @texe.decorators.enforce
        def fct(a: texe.annotations.Checks[lambda a: a != 0], *args):
            return a, *args

        assert fct(1, 2, 3, 4) == (1, 2, 3, 4)

        with pytest.raises(ValueError):
            fct(0, 1)


class TestHooks:
    def test_basic(self):
        def hookfct(parameter):
            if parameter == 0:
                raise ValueError("Hook failed!")
            return (parameter + 1)**2

        @texe.decorators.enforce
        def fct(a: texe.annotations.Hooks[int, hookfct]) -> int:
            return a

        assert fct(1) == 4
        assert fct(2) == 9

        with pytest.raises(ValueError):
            fct(0)

    def test_returns(self):
        @texe.decorators.enforce
        def abs_fct(a: int) -> texe.annotations.Hooks[lambda a: abs(a)]:
            return a

        assert abs_fct(1) == 1
        assert abs_fct(-1) == 1


class TestSequence:
    def test_base(self):
        @texe.decorators.enforce
        def foo(
                a: texe.annotations.Sequence[
                    int,
                    texe.annotations.Checks[lambda a: a != 0],
                    texe.annotations.Hooks[lambda a: a + 1],
                    texe.annotations.Checks[lambda a: a % 2 == 0]
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
                return texe.early_return.EarlyReturn(0.)   # just to check that the Check isn't triggered
            return parameter

        @texe.decorators.enforce
        def foo(
                a: texe.annotations.Sequence[
                    texe.annotations.Hooks[none_to_one],
                    texe.annotations.Checks[lambda a: a != 0]   # should never raise ValueError
                ]
        ):
            return a + 1.   # Just to make sure that this isn't triggered when EarlyReturn is used

        assert foo(1.) == 2.
        assert foo(0.) == 0.

    def test_in_different_positions(self):
        def hook1(p):
            if p == 0.:
                return texe.early_return.EarlyReturn(0.)
            return p

        def hook2(p):
            if p == 2.:
                return texe.early_return.EarlyReturn(4.)   # To see if calculation happens after function body
            return p

        @texe.decorators.enforce
        def foo(
                a: texe.annotations.Hooks[hook1] = texe.early_return.EarlyReturn(-1.), /   # to test if it works positional only
        ) -> texe.annotations.Hooks[hook2]:
            return a + 1.

        assert foo() == -1.  # default EarlyReturn
        assert foo(0.) == 0.   # EarlyReturn from hook1
        assert foo(1.) == 4.   # EarlyReturn from hook2 (1. after hook1; 2. after fct body; 4. after hook2)
        assert foo(2.) == 3.   # regular function
