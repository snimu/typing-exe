import typing
import parameter_checks as pc


class TestChecks:
    def test_construction(self):
        def check_fct(a):
            return a < 1
        checks = pc.annotations.Checks[int, check_fct]
        assert checks.checks == [check_fct]
        assert checks.typehint is int

    def test_construction_invalid_inputs(self):
        for inputs in ((1, ), (1, 2, 3)):
            checks = pc.annotations.Checks[inputs]
            assert checks.checks is None
            assert checks.typehint is None

    def test_construction_just_type(self):
        checks = pc.annotations.Checks[int]
        assert checks.checks is None
        assert checks.typehint is int

    def test_construction_just_checks(self):
        def check_fct(a):
            return a < 1

        checks = pc.annotations.Checks[check_fct]
        assert checks.checks == (check_fct, )
        assert checks.typehint is None

    def test_construction_empty(self):
        checks = pc.annotations.Checks
        assert checks.checks is None
        assert checks.typehint is None

    def test_construction_multiple_typehints_in_checks(self):
        def check_fct(a):
            return a != 0

        checks = pc.annotations.Checks[
            int, typing.Union[int, float], typing.Tuple[int, int],
            check_fct
        ]

        assert checks.typehint is int
        assert checks.checks == [check_fct]


class TestHook:
    def test_construction(self):
        hooks = pc.annotations.Hooks[lambda x: x**2, lambda x: x - 2]

        assert hooks.hooks[0](2) == 4
        assert hooks.hooks[1](2) == 0
