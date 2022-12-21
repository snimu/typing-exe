# parameter-checks

Extend typehints to include dynamic checks (that might otherwise be dealt with by assertions) in Python.

**Project**

![PyPI Version](https://img.shields.io/pypi/v/parameter_checks)
![Wheel](https://img.shields.io/pypi/wheel/parameter_checks)

**Tests**

![Tests](https://github.com/snimu/parameter-checks/actions/workflows/tests.yml/badge.svg)
![Coverage](coverage.svg)

**Misc**

![License](https://img.shields.io/github/license/snimu/parameter-checks)
![Python Versions](https://img.shields.io/pypi/pyversions/parameter_checks)

**Installation: Pip**

```bash
pip install parameter-checks
```

**Comments**

- A proper documentation is (likely) coming
- A conda-build may or may not come

**Table of Contents**

- [Package](#package)
  - [pc.annotations.Checks](#pcannotationschecks)
    - [Construction](#checks--construction)
    - [Failure](#checks--failure)
    - [Example](#checks--example)
    - [Notes](#checks--notes)
  - [pc.annotations.Hooks](#pcannotationshooks)
    - [Construction](#hooks--construction)
    - [Example 1](#hooks--example-1)
    - [Example 2](#hooks--example-2)
    - [Notes](#hooks--notes)
  - [@pc.hints.enforce](#pchintsenforce)
  - [@pc.hints.cleanup](#pchintscleanup)
- [But why?](#but-why)
- [Ideas for extensions](#ideas-for-future-extensions)
  - [Early Returns](#early-returns)
  - [Inter-argument checks and hooks](#inter-parameter-checks-and-hooks)

# Package

Basic example:

```python 
import parameter_checks as pc


@pc.hints.cleanup   # be left with only type-annotations
@pc.hints.enforce   # enforce the lambda but not the types
def div(a: int, b: pc.annotations.Checks[int, lambda b: b != 0]):
    return a / b 

div(1, 1)   # returns 1.0
div(1, 0)   # raises ValueError
```

As can be seen in this example, this package provides a new type-annotation: [pc.annotations.Checks](#pcannotationschecks)
(it also provides [pc.annotations.Hooks](#pcannotationshooks), see below). 
Using [@pc.hints.enforce](#pchintsenforce) on a function will enforce the checks given to those 
annotations (but not the types). [@pc.hints.cleanup](#pchintscleanup) would produce the 
`div.__annotations__` of `{"a": int, "b": int}` in the example above.

## pc.annotations.Checks

Add simple boolean checks on your parameters or return-values.

### Checks: Construction

As seen in the [example](#example-checks), `pc.annotations.Checks` is constructed via its 
`__getitem__`-method to conform to the type-hinting from [typing](https://docs.python.org/3/library/typing.html).

The first parameter in the brackets can either be a type-hint or a callable. All others must be callables, or they will 
be ignored by [@pc.hints.enforce](#pchintsenforce) and [@pc.hints.cleanup](#pchintscleanup). Any callable is assumed 
to take one argument&mdash;the parameter&mdash;and return a `bool`. 
If that bool is `False`, a `ValueError` will be raised. These callables will be referred to as "check functions" 
from hereon out.

### Checks: Failure

Using this annotation on a parameter- or return-hint of a callable that is decorated with 
[@pc.hints.enforce](#pchintsenforce) means that the check-functions in the `Checks`-hint 
will be executed and, if they fail, will raise a ValueError.

The following code:

```python
import parameter_checks as pc


@pc.hints.enforce
def div(
        numerator: int, 
        denominator: pc.annotations.Checks[lambda denom: denom != 0]
):
    return numerator / denominator


div(1, 0)   # raises ValueError
```

Will produce the following exception: 

    <Traceback ...>
    ValueError: 
    Check failed! 
        - Callable: 
            - Name: foo
            - Module: __main__
        - Parameter: 
            - Name: denominator
            - Value: 0

### Checks: Example

```python
import parameter_checks as pc
import enum


class Status(enum.Enum):
  FAILURE = 0
  SAVED = 1
  DISPLAYED = 2


@pc.hints.cleanup  # Cleans up annotations
@pc.hints.enforce  # Enforces the checks
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

### Checks: Notes

**CAREFUL!** Do not use this hint in any other hint (like `pc.annotations.Checks | float`, 
or `tuple[pc.annotations.Check, int, int]`). Both [@pc.hints.enforce](#pchintsenforce) 
and [@pc.hints.cleanup](#pchintscleanup) will fully ignore these `pc.annotations.Checks`. 


## pc.annotations.Hooks

Hook functions to your parameters to modify them or raise exceptions before the actual 
function even starts.

### Hooks: Construction

This works similar to [pc.annotations.Checks](#pcannotationschecks), except that its check-functions work differently.

The first item in the brackets can again be a type or a callable and the rest are callables, 
but the callables are now assumed to work differently: 

- They take four arguments in the following order: 
  1. **fct**: the function that was decorated by [@pc.hints.enforce](#pchintsenforce)
  2. **parameter**: the value of the parameter that is annotated
  3. **parameter_name**: the name of that parameter
  4. **typehint**: the typehint
- They return the parameter (as modified by the hook)
- If there are multiple hooks, they will be executed in the order in which they were given to `Hooks`. 
Each hook then executes on the output of the previous hook.

### Hooks: Example 1

```python 
import torch
import torchvision as tv
import parameter_checks as pc


transforms =  tv.transforms.Compose([
    tv.transforms.ToPILImage(), 
    tv.transforms.ToTensor(),
    tv.transforms.Normalize(mean=train_mean, std=train_std),
    tv.transforms.RandomHorizontalFlip(),
    tv.transforms.RandomVerticalFlip()
])


class Model(torch.nn.Module):
    def __init__(self):
        ...

    @pc.hints.enforce
    def forward(self, tensor: pc.annotations.Hooks[transforms]):
        ...
```

Yes, this could (and should) have been taken care of by the dataloader. 

However, applying the transforms in the function-signature might allow 
different models to use the same dataloader but with
different transforms. It would make it obvious which transform belongs to which model 
in the function-signature, instead of having to look it up in the 
dataloader. If the `transforms` were properly named, it might make the code more 
readable.

This might not be the most practical example, but it hopefully serves as inspiration.

### Hooks: Example 2

```python
import parameter_checks as pc


def hook_function(fct, parameter, parameter_name, typehint):
    if type(parameter) is not typehint:
        err_str = f"In function {fct}, parameter {parameter_name}={parameter} " \
                  f"is not of type {typehint}!"
        raise TypeError(err_str)
    
    # Yes, the following calculation should be in the function-body,
    #   but it demonstrates that arbitrary changes can be made here,
    #   which might be useful if, for example, some conversion has 
    #   to happen in many parameters of many functions. 
    # Moving that conversion into its own function and calling it 
    #   in the typehint might make the program more readable than 
    #   packing it into the function-body.
    return 3 + 4 * parameter - parameter**2   


@pc.hints.enforce
def foo(a: pc.annotations.Hooks[int, hook_function]):
    return a 


assert foo(1) == 6
assert foo(2) == 7
assert foo(5) == -2
```

### Hooks: Notes

You can also use multiple hook-functions, which will be called on each other's output in the order
in which they are given to `pc.annotations.Hooks`.

**CAREFUL!** Do not use this hint in any other hint (like `pc.annotations.Hooks | float`, 
or `tuple[pc.annotations.Hooks, int, int]`). Both [@pc.hints.enforce](#pchintsenforce) 
and [@pc.hints.cleanup](#pchintscleanup) will fully ignore these `pc.annotations.Hooks`.

## @pc.hints.enforce

This decorator enforces the two above-mentioned hints ([pc.annotations.Checks](#pcannotationschecks) 
and [pc.annotations.Hooks](#pcannotationshooks)) for a callable. 

**CAREFUL!** This decorator *doesn't* enforce type-hints, but only the check- and hook-functions. 
Type-hints are only there for [@pc.hints.cleanup](#pchintscleanup).

## @pc.hints.cleanup

This decorator removes any hint of `pc.annotations.Checks` (and `pc.annotations.Hooks`, as described below). This means that a 
function annotated as follows:

```python 
import parameter_checks as pc 


@pc.hints.cleanup
@pc.hints.enforce
def foo(
        a: int, 
        b: pc.annotations.Checks[int, ...], 
        c
) -> pc.annotations.Checks[...]:
    ...
```

which is excpected to have the following `__annotations__`: 

`{'a': int, 'b': pc.annotations.Checks[int, ...], 'return': pc.annotations.Checks[...]`

now actually has these annotations:

`{'a': int, 'b': int}`

This way, other decorators can work as usual. 

This decorator is separate from 
[@pc.hints.enforce](#pchintsenforce) so that users can decide to somehow make use
of [pc.annotations.Checks](#pcannotationschecks) and [pc.annotations.Hooks](#pcannotationshooks)
in their own functions or decorators, or choose to remove those pesky annotations and have 
normal-looking `__annotations__`.

# But why?

Few things are more useful in programming than the ability to constrain a program's possible behaviors 
and communicate those constraints clearly in code. Statically typed languages do this with types, scope modifiers, 
and lifetime modifiers, among others (`int`, `static`, `private`, `const`, etc.). These are static constraints 
in that they are evaluated statically, before runtime.

Oftentimes, a program also has dynamic constraints, evaluated during runtime&mdash;assertions, for example. 
A function dealing with division, for example, has to deal with the special case of division by zero.

Replacing parameter-checks in the function-body with enforceable typehints in the 
function-signature might have the following advantages:

- Make code more readable by having constraints in a predefined place
- Encourage programmers to think about these constraints while writing the functions&mdash;a type of 
test-driven development directly at the function (seeing parts of the "tests" in the function-signature
might assist readability of code, as well)
- Make code easier to write by providing important information about APIs in a glancable way
  - This would of course require editor-support, which I do not provide
- Make it possible to include information on dynamic constraints in automatically generated documentation


# Ideas for future extensions

There is still a lot that this package cannot do, and here are some ideas about how to address this.

Feedback on these ideas (as well as other contributions, of course) is welcome.

## Early returns

Many checks in functions trigger early returns. While this could theoretically be achieved with 
[pc.annotations.Hooks](#pcannotationshooks) by changing the parameter into a special value, 
being more explicit about this might be helpful. This could look as follows:

```python 
import parameter_checks as pc


def hook_with_early_return(fct, parameter, parameter_name, typehint):
    if ...:
        # Ignore all other hooks and the function-body;
        #   just return the values in EarlyReturn 
        return pc.annotations.EarlyReturn["well, this did not work out"]
    ...


@pc.hints.enforce
def foo(a: pc.annotations.Hooks[int, hook_with_early_return]):
    # If a is of the wrong value, this part is never called;
    #   instead, "well, this did not work out" will be returned 
    #   immediately
    ...
```

## Inter-parameter Checks and Hooks

Many checks compare two or more parameters; this can currently not be done with this package.
One possibility for how it could be achieved is shown in the following example:

```python
import parameter_checks as pc


@pc.hints.enforce
def foo(
        a, 
        b: pc.annotations.Checks[
            int,
            pc.annotations.CompareWith[
                "a", lambda b, a: b < a   # should take arbitrary number of args
            ]
        ]
):
    ...


# Bigger example
@pc.hints.enforce
def bar(
        a, 
        b,
        c: pc.annotations.Checks[
            pc.annotations.CompareWith[
                "a", "b", lambda c, a, b: a < b < c 
            ]
        ],
        d: pc.annotations.Hooks[
            pc.annotations.CompareWith[
                "a", "b", "c", comparison_hook
            ]
        ]
):
    ...


def comparison_hook(fct, parameters: list, parameter_names: list, typehint):
    d, a, b, c = parameters 
    dname, aname, bname, cname = parameter_names
    ...
```
