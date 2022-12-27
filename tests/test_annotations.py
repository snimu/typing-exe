import inspect
import typing
import pytest

from typing_exe.annotations import Assert, Modify


class TestChecks:
    def test_construction(self):
        def check_fct(a):
            return a < 1
        checks = Assert[int, check_fct]
        assert isinstance(checks.items.get(check_fct), inspect.Signature)
        assert checks.typehint is int

    def test_construction_invalid_inputs(self):
        for inputs in ((1, ), (1, 2, 3)):
            checks = Assert[inputs]
            assert checks.items is None
            assert checks.typehint is None

    def test_construction_just_type(self):
        checks = Assert[int]
        assert checks.items is None
        assert checks.typehint is int

    def test_construction_just_checks(self):
        def check_fct(a):
            return a < 1

        checks = Assert[check_fct]
        assert isinstance(checks.items.get(check_fct), inspect.Signature)
        assert checks.typehint is None

    def test_construction_empty(self):
        checks = Assert

        with pytest.raises(AttributeError):
            items = checks.items

        with pytest.raises(AttributeError):
            checks.items = 1

    def test_construction_multiple_typehints_in_checks(self):
        def check_fct(a):
            return a != 0

        checks = Assert[
            int, typing.Union[int, float], typing.Tuple[int, int],
            check_fct
        ]

        assert checks.typehint is int
        assert isinstance(checks.items.get(check_fct), inspect.Signature)


class TestHook:
    def test_construction(self):
        hooks = Modify[lambda x: x ** 2, lambda x: x - 2]

        mod1, mod2 = hooks.items.keys()
        assert mod1(2) == 4
        assert mod2(2) == 0
