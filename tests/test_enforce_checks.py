import pytest
import parameter_checks as pc


def test_basic():
    @pc.hints.enforce
    def fct(a: pc.annotations.Checks[int, lambda a: a < 5]):
        return a

    assert fct(1) == 1

    with pytest.raises(ValueError):
        fct(5)


def test_multiple():
    @pc.hints.enforce
    def fct(
            a: pc.annotations.Checks[lambda a: a != 0, lambda a: a%3 == 0],
            b: int,
            c,
            d: pc.annotations.Checks[int] = None
    ):
        return a, b, c, d

    assert fct(3, 1, 1) == (3, 1, 1, None)
    assert fct(6, b=1, c=1, d=1) == (6, 1, 1, 1)

    with pytest.raises(ValueError):
        fct(0, 1, 1, 1)

    with pytest.raises(ValueError):
        fct(1, 1, 1, 1)
