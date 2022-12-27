from typing import Union
import pytest

from typing_exe.annotations import Assert, Sequence, Modify
from typing_exe.decorators import execute_annotations, cleanup_annotations


def test_cleanup():
    @cleanup_annotations
    @execute_annotations
    def fct(
            a: Assert[lambda a: a > 0],
            b: float,
            c: Assert[int, lambda c: c != 0],
            d,
            e: Union[int, float],
            f: Sequence[
                int,
                Assert[lambda a: a != 0],
                Modify[lambda a: a + 1]
            ]
    ) -> Modify[int]:
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
