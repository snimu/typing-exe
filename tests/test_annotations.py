import typing

import pytest

import typing_exe as texe


class TestChecks:
    def test_construction(self):
        def check_fct(a):
            return a < 1
        checks = texe.annotations.Assert[int, check_fct]
        assert checks.items == [check_fct]
        assert checks.typehint is int

    def test_construction_invalid_inputs(self):
        for inputs in ((1, ), (1, 2, 3)):
            checks = texe.annotations.Assert[inputs]
            assert checks.items is None
            assert checks.typehint is None

    def test_construction_just_type(self):
        checks = texe.annotations.Assert[int]
        assert checks.items is None
        assert checks.typehint is int

    def test_construction_just_checks(self):
        def check_fct(a):
            return a < 1

        checks = texe.annotations.Assert[check_fct]
        assert checks.items == (check_fct,)
        assert checks.typehint is None

    def test_construction_empty(self):
        checks = texe.annotations.Assert

        with pytest.raises(AttributeError):
            items = checks.items

        with pytest.raises(AttributeError):
            checks.items = 1

    def test_construction_multiple_typehints_in_checks(self):
        def check_fct(a):
            return a != 0

        checks = texe.annotations.Assert[
            int, typing.Union[int, float], typing.Tuple[int, int],
            check_fct
        ]

        assert checks.typehint is int
        assert checks.items == [check_fct]


class TestHook:
    def test_construction(self):
        hooks = texe.annotations.Modify[lambda x: x ** 2, lambda x: x - 2]

        assert hooks.items[0](2) == 4
        assert hooks.items[1](2) == 0
