from typing import Union
import pytest
import parameter_checks as pc


def test_cleanup():
    @pc.hints.cleanup
    @pc.hints.enforce
    def fct(
            a: pc.annotations.Checks[lambda a: a > 0],
            b: float,
            c: pc.annotations.Checks[int, lambda c: c != 0],
            d,
            e: Union[int, float]
    ) -> pc.annotations.Hooks[int]:
        return int(a + b + c + d + e)

    # Check that enforce works:
    assert fct(1, 1, 1, 1, 1) == 5

    with pytest.raises(ValueError):
        fct(0, 1, 1, 1, 1)

    with pytest.raises(ValueError):
        fct(1, 1, 0, 1, 1)

    # Check that annotations are fine
    assert fct.__annotations__ == {"b": float, "c": int, "e": Union[int, float], "return": int}
