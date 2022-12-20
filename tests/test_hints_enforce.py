import pytest
import parameter_checks as pc
from typing import Union


class TestChecks:
    def test_basic(self):
        @pc.hints.enforce
        def fct(a: pc.annotations.Checks[int, lambda a: a < 5]):
            return a

        assert fct(1) == 1

        with pytest.raises(ValueError):
            fct(5)

    def test_multiple(self):
        @pc.hints.enforce
        def fct(
                a: pc.annotations.Checks[lambda a: a != 0, lambda a: a%3 == 0],
                b: int,
                c,
                d: pc.annotations.Checks[int] = None
        ):
            return a, b, c, d

        assert fct(3, 1, 1) == (3, 1, 1, None)
        assert fct(6, b=1, c=1, d=1) == (6, 1, 1, 1)

        with pytest.raises(ValueError):
            fct(0, 1, 1, 1)

        with pytest.raises(ValueError):
            fct(1, 1, 1, 1)

    def test_typing(self):
        @pc.hints.enforce
        def fct(a: pc.annotations.Checks[Union[int, float], lambda a: a != 0]):
            return a

        assert fct(1) == 1

        with pytest.raises(ValueError):
            fct(0)


class TestHooks:
    def test_basic(self):
        def hookfct(fct, parameter, parameter_name, typehint):
            if parameter == 0:
                raise ValueError("Hook failed!")
            return (parameter + 1)**2

        @pc.hints.enforce
        def fct(a: pc.annotations.Hooks[int, hookfct]):
            return a

        assert fct(1) == 4
        assert fct(2) == 9

        with pytest.raises(ValueError):
            fct(0)
