# parameter-checks

Add checks to parameters (and return values) to functions. 

**Project**

![PyPI Version](https://img.shields.io/pypi/v/parameter_checks)
![Wheel](https://img.shields.io/pypi/wheel/parameter_checks)

**Tests**

![Tests](https://github.com/snimu/parameter-checks/actions/workflows/tests.yml/badge.svg)
![Coverage](coverage.svg)

**Misc**

![License](https://img.shields.io/github/license/snimu/parameter_checks)
![Python Versions](https://img.shields.io/pypi/pyversions/parameter_checks)

**Installation: Pip**

```bash
pip3 install parameter_checks
```

## Design

Should work something like this:

```python
import parameter_checks as pc
import enum


class Status(enum.Enum):
  FAILURE = 0
  SAVED = 1
  DISPLAYED = 2


@pc.enforce.cleanup  # Cleans up annotations
@pc.enforce.enforce  # Enforces the checks
def function(
        rescale: pc.annotations.Checks[
          float,
          lambda a: 1. < a < 25.
        ],
        file: pc.annotations.Checks[
          str,
          lambda file: file.endswith(".jpg") or file.endswith(".png"),
          lambda file: not file.endswith("private.jpg") and not file.endswith("private.jpg"),
          lambda file: not file.startswith("_")
        ]
) -> pc.annotations.Checks[Status, lambda r: r != Status.FAILURE]:
  ...
```

### Rules

- The first entry in `Checks` can either be a type or a callable. All others have to be callables. 
- Not all annotations have to be `Checks`. If it is a type-annotation, it will be enforced.
  - Always allow None, obviously. 
- `@pc.annotations.cleanup` is independent of `@pc.enforce.checks` so that other decorators may be able to work with 
the full annotation-data in the future. 


### Plan

- At first, only implement the checks (because it is much easier).
- Types in `Checks` are only there for `@pc.enforce.cleanup` to work.

