from concurrent.futures import ThreadPoolExecutor
import parameter_checks as pc
import pytest


def test_checks_threaded():
    @pc.hints.enforce
    def threaded_function(a: pc.annotations.Checks[lambda a: a != 0]):
        return a

    # Check if checks work non-threaded
    assert threaded_function(1) == 1
    with pytest.raises(ValueError):
        threaded_function(0)

    # Do the threaded test
    with ThreadPoolExecutor(max_workers=30) as executor:
        executor.map(threaded_function, range(1, 31))

def test_hooks_threaded():
    @pc.hints.enforce
    def threaded_function(
            a: pc.annotations.Hooks[
                lambda f, p, pn, t: p + 1,
                lambda f, p, pn, t: p**2
            ]
    ):
        return a

    # Check that it works non-threaded
    assert threaded_function(1) == 4
    assert threaded_function(2) == 9

    with ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(threaded_function, range(30))

    for i, result in enumerate(results):
        assert result == (i + 1)**2