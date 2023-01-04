![PyPI Version](https://img.shields.io/pypi/v/parameter_checks)
![Tests](https://github.com/snimu/typing-exe/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/github/license/snimu/typing-exe)

# typing-exe

Executable typehints for Python: make assertions about and/or modify parameters & return values.

**GitHub page:** [snimu/typing-exe](https://github.com/snimu/typing-exe)

## Example

```python
from typing_exe.annotations import Assert, Modify
from typing_exe.decorators import execute_annotations, cleanup_annotations


@cleanup_annotations
@execute_annotations
def divide(
        a: Modify[lambda a: float(a)], 
        b: Assert[float, lambda b: b != 0]
) -> float:
    return a / b
```

What's going on here?

From the bottom to the top:

- The function `divide` divides two numbers
- Its parameters have executable annotations:
  - `a` is annotated by `Modify`. This means that when `divide` is called, 
before the function-body is executed, `a` is cast to `float`
  - `b` is annotated by `Assert`. This means that when `divide` is called,
before the function-body is executed, a check runs and raises a `ValueError` 
if `b` is zero
- [@execute_annotations](https://snimu.github.io/typing-exe/execute_annotations/) 
enables the execution of these decorators. Without it, the annotations are in the way.
- [@cleanup_annotations](https://snimu.github.io/typing-exe/cleanup_annotations/)
removes the `Modify` and `Assert` from the function's annotations so that `divide` 
can for used by other tools like [strongtyping](https://github.com/FelixTheC/strongtyping). 

## But why?

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