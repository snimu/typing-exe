from concurrent.futures import ThreadPoolExecutor
import typing_exe as texe
import pytest


def test_checks_threaded():
    @texe.decorators.enforce
    def threaded_function(a: texe.annotations.Checks[lambda a: a != 0]):
        return a

    # Check if checks work non-threaded
    assert threaded_function(1) == 1
    with pytest.raises(ValueError):
        threaded_function(0)

    # Do the threaded test
    with ThreadPoolExecutor(max_workers=30) as executor:
        executor.map(threaded_function, range(1, 31))

def test_hooks_threaded():
    @texe.decorators.enforce
    def threaded_function(
            a: texe.annotations.Hooks[
                lambda p: p + 1,
                lambda p: p**2
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