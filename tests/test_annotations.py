import pytest
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

    def test_construction_empty(self):
        checks = pc.annotations.Checks
        assert checks.checks is None
        assert checks.typehint is None


class TestHook:
    def test_construction(self):
        def check_fct(a):
            return a < 1

        def hook_fct(a):
            return 0

        hook = pc.annotations.Hook[check_fct, hook_fct, "Not a real Hook"]
        assert isinstance(hook, pc.annotations._Hook)
        assert hook.check is check_fct
        assert hook.hook is hook_fct
        assert hook.description == "Not a real Hook"
