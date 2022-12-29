# Assert

Add simple boolean checks on your parameters or return-values.
    
## Simple example

Below is the simple example of a constrained division-function.

### The example
    
```python
from typing_exe.annotations import Assert
from typing_exe.decorators import execute_annotations, cleanup_annotations

@cleanup_annotations
@execute_annotations
def divide(
           a: Assert[lambda a: a >= 0], 
           b: Assert[float, lambda b: b != 0]
) -> Assert[lambda r, a, b: r < a if b > 1 else r >= a]:
     return a / b
```   

### Explanation

What happens when `divide` is called? 

1. The first `Assert` is checked. If `a` is smaller than 0, a `ValueError` is raised
2. The second `Assert` is checked. If `b` is equal to 0, a `ValueError` is raised
3. The function-body is executed and the result of `a / b` calculated
4. Its result is checked for plausibility by the third `Assert`
5. The result is returned
        
## Description
        
As the two typehints in the example above show, the first entry can either be a typehint, 
or an assertion. All other entries are assertions (an arbitrary number of them).
    
The typehint will be ignored by Assert. Its purpose is twofold: Firstly, it helps readability.
Secondly, when [@execute_annotations](https://snimu.github.io/typing-exe/execute_annotations/) 
is paired with [@cleanup_annotations](https://snimu.github.io/typing-exe/cleanup_annotations/), 
only that typehint will be left in the function's annotations, so that the function can be used 
properly by other packages such as [strongtyping](https://github.com/FelixTheC/strongtyping).
    
The assertions are not in the form of `assert`-statements but in the form of functions that 
take the parameter and return a boolean value. If that boolean value is `False`, a `ValueError` 
will be raised (this only works if your function, foo in the example above, is decorated with 
@execute_annotations). 
    
It is also possible to make comparisons with other parameters by simply giving your assertion-function
more than one parameter, where the first parameter is assumed to be the one that is annotated, 
while the others are the other parameters. It is important that those parameters are called the 
same in both the assertion-function (the lambda in the return-annotation in the example) and 
the annotated function (`divide` in the example above). The name of the parameter itself in the 
assertion-function is irrelevant but should, for readability, usually be the same as the parameter
that is annotated by this assertion-function.
    
For example, the following works:
    
```python
from typing_exe.annotations import Assert


def foo(a, b: Assert[lambda whatever, a: whatever > a]):
    ...
```
        
But this doesn't:
    
```python
from typing_exe.annotations import Assert


def foo(a, b: Assert[lambda b, whatever: b > whatever]):
    ...
```
    
Good form would be the following:
    
```python
from typing_exe.annotations import Assert


def foo(a, b: Assert[lambda b, a: b > a]):
     ...
```
        
Of course, the assertion-functions don't have to be lambdas. 

## Larger example

```python
...
```
    