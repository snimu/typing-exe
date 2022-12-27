from typing import Union
import pytest
import typing_exe as texe


def test_cleanup():
    @texe.hints.cleanup
    @texe.hints.enforce
    def fct(
            a: texe.annotations.Checks[lambda a: a > 0],
            b: float,
            c: texe.annotations.Checks[int, lambda c: c != 0],
            d,
            e: Union[int, float]
    ) -> texe.annotations.Hooks[int]:
        return int(a + b + c + d + e)

    # Check that enforce works:
    assert fct(1, 1, 1, 1, 1) == 5

    with pytest.raises(ValueError):
        fct(0, 1, 1, 1, 1)

    with pytest.raises(ValueError):
        fct(1, 1, 0, 1, 1)

    # Check that annotations are fine
    assert fct.__annotations__ == {"b": float, "c": int, "e": Union[int, float], "return": int}
