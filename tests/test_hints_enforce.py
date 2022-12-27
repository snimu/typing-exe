import pytest
import typing_exe as texe
from typing import Union


class TestChecks:
    def test_basic(self):
        @texe.hints.enforce
        def fct(a: texe.annotations.Checks[int, lambda a: a < 5]):
            return a

        assert fct(1) == 1

        with pytest.raises(ValueError):
            fct(5)

    def test_multiple(self):
        @texe.hints.enforce
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
        @texe.hints.enforce
        def fct(a: texe.annotations.Checks[Union[int, float], lambda a: a != 0]):
            return a

        assert fct(1) == 1

        with pytest.raises(ValueError):
            fct(0)

    def test_return(self):
        @texe.hints.enforce
        def faulty_abs(a: int) -> texe.annotations.Checks[lambda r: r >= 0]:
            return a

        assert faulty_abs(1) == 1

        with pytest.raises(ValueError):
            faulty_abs(-1)

    def test_args_without_typehints(self):
        @texe.hints.enforce
        def div(a, b: texe.annotations.Checks[lambda b: b != 0]):
            return a / b

        assert div(1, 1) == 1.

        with pytest.raises(ValueError):
            div(1, 0)

    def test_with_default_value(self):
        def none_to_one(fct, parameter, parameter_name, typehint):
            if parameter is not None:
                assert type(parameter) is typehint

            parameter = 1. if parameter is None else parameter
            return parameter

        @texe.hints.enforce
        def div(a, b: texe.annotations.Hooks[float, none_to_one] = None):
            return a / b

        assert div(2., 2.) == 1.
        assert div(2., None) == 2.
        assert div(2.) == 2.

        with pytest.raises(AssertionError):
            div(2., "not a float!")

    def test_with_star_args_fct(self):
        @texe.hints.enforce
        def fct(a: texe.annotations.Checks[lambda a: a != 0], *args):
            return a, *args

        assert fct(1, 2, 3, 4) == (1, 2, 3, 4)

        with pytest.raises(ValueError):
            fct(0, 1)


class TestHooks:
    def test_basic(self):
        def hookfct(fct, parameter, parameter_name, typehint):
            if parameter == 0:
                raise ValueError("Hook failed!")
            return (parameter + 1)**2

        @texe.hints.enforce
        def fct(a: texe.annotations.Hooks[int, hookfct]) -> int:
            return a

        assert fct(1) == 4
        assert fct(2) == 9

        with pytest.raises(ValueError):
            fct(0)

    def test_returns(self):
        def hookfct(fct, parameter, parameter_name, typehint):
            return abs(parameter)

        @texe.hints.enforce
        def abs_fct(a: int) -> texe.annotations.Hooks[hookfct]:
            return a

        assert abs_fct(1) == 1
        assert abs_fct(-1) == 1
