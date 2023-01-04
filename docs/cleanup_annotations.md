# cleanup_annotations

Remove annotations from the `typing-exe` package to leave your function with clean `__annotations__`.

## Example

```python 
from typing_exe.annotations import Assert, Modify, Sequence
from typing_exe.decorators import execute_annotations, cleanup_annotations


@cleanup_annotations
@execute_annotations
def foo(
        a: int, 
        b, 
        c: Assert[lambda c: c > 5], 
        d: Modify[int, lambda d: d / 2]
) -> Sequence[
        str, 
        Assert[lambda r: len(r) < 20], 
        Modify[lambda r: r if r.endswith(".pdf") else r + ".pdf"]
]:
    ...


# foo.__annotations__: {'a': <class 'int'>, 'd': <class 'int'>, 'return': <class 'str'>}
```

## Explanation 

Without `@cleanup_annotations`, `foo.__annotations__` from the example above 
would be very complex and&mdash;importantly&mdash;unusable
for other packages such as [strongtyping](https://github.com/FelixTheC/strongtyping). With it, they are 
`{'a': <class 'int'>, 'd': <class 'int'>, 'return': <class 'str'>}`.
[@execute_annotations](https://snimu.github.io/typing-exe/execute_annotations/) does not automatically do this 
so that users can, if they want to, not use `@cleanup_annotations` and work with the annotations that include
[Assert](https://snimu.github.io/typing-exe/assert/), [Modify](https://snimu.github.io/typing-exe/modify/), 
and [Sequence](https://snimu.github.io/typing-exe/sequence/). 

### Caveat

`@cleanup_annotations` does not go into your annotations recursively. If you have one of the annotations from 
`typing-exe` inside of a regular typehint&mdash;for example, `Union[int, Assert[...]]`&mdash;then it will not be
removed. 

In other words, **only use [Assert](https://snimu.github.io/typing-exe/assert/), 
[Modify](https://snimu.github.io/typing-exe/modify/), and [Sequence](https://snimu.github.io/typing-exe/sequence/)
directly, not inside other annotations.**
