![Wheel](https://img.shields.io/pypi/wheel/parameter_checks)
![Tests](https://github.com/snimu/parameter-checks/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/github/license/snimu/parameter-checks)
![Python Versions](https://img.shields.io/pypi/pyversions/parameter_checks)


For more info, please [visit the GitHub page of this project](https://github.com/snimu/parameter-checks).

### Basic example


```python 
import parameter_checks as pc


@pc.hints.cleanup   # be left with only type-annotations
@pc.hints.enforce   # enforce the lambda but not the types
def div(a: int, b: pc.annotations.Checks[int, lambda b: b != 0]):
    return a / b 

div(1, 1)   # returns 1.0
div(1, 0)   # raises ValueError
```

As can be seen in this example, this package provides a new type-annotation: 
[pc.annotations.Checks](https://github.com/snimu/parameter-checks#pcannotationschecks)
(it also provides [pc.annotations.Hooks](https://github.com/snimu/parameter-checks#pcannotationshooks), see below). 
Using [@pc.hints.enforce](https://github.com/snimu/parameter-checks#pchintsenforce) on a function 
will enforce the checks given to those annotations (but not the types). 
[@pc.hints.cleanup](https://github.com/snimu/parameter-checks#pchintscleanup) would produce the 
`div.__annotations__` of `{"a": int, "b": int}` in the example above.


### Complex example

```python
import parameter_checks as pc


def decision_boundary(fct, parameter, parameter_name, typehint):
    if type(parameter) is not typehint:
        err_str = f"In function {fct}, parameter {parameter_name}={parameter} " \
                  f"is not of type {typehint}!"
        raise TypeError(err_str)
    
    return 3 + 4 * parameter - parameter ** 2


@pc.hints.enforce
def classify(
        x: pc.annotations.Hooks[float, decision_boundary],
        additional_offset: pc.annotations.Checks[float, lambda b: 0 <= b <= 100] = 0.
) -> bool:
  return (x + additional_offset) >= 0


assert classify(1.) is True   # 6.
assert classify(2.) is True   # 7.
assert classify(5.) is False   # -2.
assert classify(5., 2.) is True   # 0.

classify("not a float!")  # raises TypeError
classify(1., -1.)   # raises ValueError
```
