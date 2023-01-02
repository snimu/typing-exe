# Sequence

String together [Assert](https://snimu.github.io/typing-exe/assert/) 
and [Modify](https://snimu.github.io/typing-exe/modify/)
annotations.

## Basic example

### The example

```python
from typing_exe.annotations import Sequence, Assert, Modify
from typing_exe.decorators import execute_annotations, cleanup_annotations


@cleanup_annotations
@execute_annotations
def foo(
        a: Sequence[
            int,
            Assert[lambda a: type(a) is int, lambda a: a != 0],
            Modify[lambda a: abs(a)],
            Assert[lambda a: a > 5]
        ]
):
    ...
```

### Explanation

When `foo` gets executed, the following will happen:

1. The first `Assert` will check `a`'s type, then check that it is not zero
2. The `Modify` will then return the absolute value of `a`
3. The second `Assert` will check that `a` is now greater than five
4. The function-body will be executed

## Description

The first entry to the `Sequence.__getitem__`-method can either be a typehint or an 
[Assert](https://snimu.github.io/typing-exe/assert/) or [Modify](https://snimu.github.io/typing-exe/modify/).
All other entries have to be either an `Assert` or a `Modify`.

Here are some legal calls to `Sequence`:

```python
from typing_exe.annotations import Sequence, Assert, Modify


Sequence[int, Assert[...], Modify[...]]
Sequence[Assert[...], Modify[...]]
Sequence[Modify[...], Modify[...], Modify[...]]
Sequence[str, Modify[...]]
Sequence[Assert[...]]   # not very useful
```
