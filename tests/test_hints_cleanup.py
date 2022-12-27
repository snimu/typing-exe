from typing import Union
import pytest
import typing_exe as texe


def test_cleanup():
    @texe.decorators.cleanup_annotations
    @texe.decorators.execute_annotations
    def fct(
            a: texe.annotations.Assert[lambda a: a > 0],
            b: float,
            c: texe.annotations.Assert[int, lambda c: c != 0],
            d,
            e: Union[int, float],
            f: texe.annotations.Sequence[
                int,
                texe.annotations.Assert[lambda a: a != 0],
                texe.annotations.Modify[lambda a: a + 1]
            ]
    ) -> texe.annotations.Modify[int]:
        return int(a + b + c + d + e + f)

    # Check that enforce works:
    assert fct(1, 1, 1, 1, 1, 1) == 7

    with pytest.raises(ValueError):
        fct(0, 1, 1, 1, 1, 1)

    with pytest.raises(ValueError):
        fct(1, 1, 0, 1, 1, 1)

    with pytest.raises(ValueError):
        fct(1, 1, 1, 1, 1, 0)

    # Check that annotations are fine
    assert fct.__annotations__ == {"b": float, "c": int, "e": Union[int, float], "f": int, "return": int}
