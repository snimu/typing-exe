# Quickstart

Welcome to [typing-exe](https://snimu.github.io/typing-exe/)! 

**Installation**

```bash
pip install typing-exe
```

**GitHub page** 

[snimu/typing-exe](https://github.com/snimu/typing-exe)

## Let's begin!

Let's just show the features provided by this package, one after the other.

##### Assert: basic

First off: [Assert](https://snimu.github.io/typing-exe/assert/).
Don't forget [@execute_annotations](https://snimu.github.io/typing-exe/execute_annotations/)
or the annotations won't do anything!

```python
from typing_exe.annotations import Assert
from typing_exe.decorators import execute_annotations


@execute_annotations
def foo(a: Assert[lambda a: a >= 0]):
    ...
```

What happens when `foo` is called? Before the function-body is executed, the parameter `a` is checked with the
given function (in this case a lambda, though it can be a regular function as long as it takes the parameter and
returns a `bool`). If that function returns `True`, then the function-body is executed, if it returns `False`, 
a `ValueError` is raised that might look something like this:

    <traceback>
    ValueError: 
    Assert failed! 
        - Callable: 
            - Name: foo
            - Module: __main__
        Assertion:
            - Name: <lambda>
            - Module: __main__
        - Parameter: 
            - Name: a
            - Value: -1

##### Assert: multiple assertions

It is easy to run an arbitrary number of assertions in succession:

```python
from typing_exe.annotations import Assert
from typing_exe.decorators import execute_annotations


@execute_annotations
def foo(a: Assert[lambda a: a >= 0, lambda a: a%3 == 0]):
    ...
```

The assertions will be checked one after the other. If one fails, a `ValueError` will be raised.


##### Assert: between parameters

It is also easy to compare one parameter to others.

```python
from typing_exe.annotations import Assert
from typing_exe.decorators import execute_annotations


@execute_annotations
def foo(a, b: Assert[lambda b, a: b > a]):
    ...
```

It is important that all names correspond to the name of the parameter they refer to. The exception is the 
annotated parameter, though it is bad form to give it some random name.

```python
from typing_exe.annotations import Assert
from typing_exe.decorators import execute_annotations


# Works, good form
@execute_annotations
def foo(a, b: Assert[lambda b, a: b > a]):
    ...


# Works, bad form
@execute_annotations
def hoo(a, b: Assert[lambda bar, a: bar > a]):
    ...


# Doesn't work
@execute_annotations
def hoo(a, b: Assert[lambda b, nope: b > nope]):
    ...
```


##### Assert: returns

Of course, all of these features are available for return values (which is the reason why 
the first parameter to an assertion does not have to be called the same as the parameter it 
annotates: it would not work for return values):

```python
from typing_exe.annotations import Assert
from typing_exe.decorators import execute_annotations


@execute_annotations
def foo(a) -> Assert[lambda r, a: r > a]:
    ...
```

This [Assert](https://snimu.github.io/typing-exe/assert/) 
will be executed after the function-body, and only then will the result be returned.


##### cleanup_annotations

These type-annotations aren't the actual types that the parameter takes; they are just a way to 
move constraints on a callable to a place where they are immediately visible to programmers. 
But what if you want to use actual typehints? Don't worry, `typing-exe` has you covered.

```python
from typing_exe.decorators import execute_annotations, cleanup_annotations
from typing_exe.annotations import Assert


@cleanup_annotations
@execute_annotations
def foo(a: Assert[int, lambda a: a != 0]):
    ...
```

Now, the [Assert](https://snimu.github.io/typing-exe/assert/)
will be executed, but `foo.__annotations__` will be `{'a': <class 'int'>}`, 
making it useful to other packages such as [strongtyping](https://github.com/FelixTheC/strongtyping).


##### Modify

[Modify](https://snimu.github.io/typing-exe/modify/) works exactly as 
[Assert](https://snimu.github.io/typing-exe/assert/) does, except that the modification functions
are expected to return the parameter&mdash;changed however you want&mdash;instead of a `bool`. 
Instead of checking the returned `bool` and raising a `ValueError` if it is `False`, 
[Modify](https://snimu.github.io/typing-exe/modify/) will change the actual parameter.

Of course, just like with [Assert](https://snimu.github.io/typing-exe/assert/), 
the modification-functions don't have to be lambdas, 
the examples below just do that for brevity.

```python
from typing_exe.annotations import Modify
from typing_exe.decorators import execute_annotations


@execute_annotations
def foo(a: Modify[lambda a: a + 1]):
    ...
```

Before the function-body of `foo` is executed, `a` is changed by adding 1 to it. The function-body
then works with that modified `a`.

Of course, all the features of [Assert](https://snimu.github.io/typing-exe/assert/)
are also available for [Modify](https://snimu.github.io/typing-exe/modify/). 
This means that multiple modifications can be done in a row in one 
[Modify](https://snimu.github.io/typing-exe/modify/)-statement, 
[Modify](https://snimu.github.io/typing-exe/modify/) works in return-annotations,
other parameters can be taken into account, 
and [@cleanup_annotations](https://snimu.github.io/typing-exe/cleanup_annotations/)
will treat [Modify](https://snimu.github.io/typing-exe/modify/) just like 
[Assert](https://snimu.github.io/typing-exe/assert/).

There is one additional tool that can be used with [Modify](https://snimu.github.io/typing-exe/modify/),
however: [EarlyReturn](https://snimu.github.io/typing-exe/early_return/).

##### EarlyReturn

Sometimes, when some condition is satisfied, you just want to return early without having to execute the rest 
of the function. `typing-exe` has you covered!

```python
from typing_exe.early_return import EarlyReturn
from typing_exe.annotations import Modify
from typing_exe.decorators import execute_annotations


def modification(a):
    if a == 0:
        return EarlyReturn(1e100)   # something / 0 is very big... Having a dedicated inf would be better
    return 1/a

@execute_annotations
def foo(a: Modify[modification]):
    ...
```

Now, `foo(0)` will immediately return `1e100` without even executing the function-body (or any of the other, 
later annotations). Annotations before the [EarlyReturn](https://snimu.github.io/typing-exe/early_return/) 
will be executed normally.

##### EarlyReturn: default value

[EarlyReturn](https://snimu.github.io/typing-exe/early_return/) can even be used as a default value!
This way, if a parameter to a function is unfilled, a default can be returned immediately. 

```python
from typing import Union
from typing_exe.early_return import EarlyReturn
from typing_exe.decorators import execute_annotations


@execute_annotations
def foo(a: Union[str, EarlyReturn] = EarlyReturn("well that was quick")):
    ...
```

If you are using type-checkers, [EarlyReturn](https://snimu.github.io/typing-exe/early_return/) of course
has to be allowed as a type to the parameter, as seen in the example above.

##### Sequence: chaining `Assert` and `Modify` statements

Do you want to assert something about a parameter, then modify it, then check the result of that modification,
then modify again, and so on, and so on? `typing-exe` has you covered!

```python
from typing_exe.annotations import (
    Assert,
    Modify,
    Sequence
)
from typing_exe.decorators import (
    execute_annotations,
    cleanup_annotations
)


@cleanup_annotations
@execute_annotations
def foo(
        a: Sequence[
            float,
            Assert[lambda a: a != 0],
            Modify[lambda a, b: b / a],
            Assert[lambda a: 0 < a < 10_000]
        ],
        b: float
):
    ...
```

