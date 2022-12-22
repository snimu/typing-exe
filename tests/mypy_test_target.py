from typing import Union
import parameter_checks as pc


# For the benefit of mypy
if __name__ == "__main__":
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


    fct(1, 1, 1, 1, 1)
