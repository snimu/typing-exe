Modify your parameters before or your return values after execution of your function-body.
    
# Usage
    
```python
from typing_exe.annotations import Modify
from typing_exe.decorators import execute_annotations, cleanup_annotations

@cleanup_annotations
@execute_annotations
def foo(
           a: Modify[lambda a: 3 + 2*a + 4*a**2 + a**3], 
           b: Modify[float, lambda b: abs(b)]
) -> Modify[lambda r, a, b: r if a + b < 10_000 else r/100]:
     return a - b
```   

The example is completely meaningless and only serves to demonstrate the how-to, not the why, of using `Modify`.
        
# Description
        
As the two typehints in the example above show, the first entry can either be a typehint, 
or a modification. All other entries are modifications (an arbitrary number of them).
    
The typehint will be ignored by Modify. Its purpose is twofold: Firstly, it helps readability.
Secondly, when @execute_annotations is paired with @cleanup_annotations, only that typehint will
be left in the function's annotations, so that the function can be used properly by other 
packages such as [strongtyping](https://github.com/FelixTheC/strongtyping).
    
The modifications are functions that 
take the parameter, modify it, and then return it 
(this only works if your function, foo in the example above, is decorated with 
@execute_annotations). 
    
It is also possible to make comparisons with other parameters by simply giving your modification-function
more than one parameter, where the first parameter is assumed to be the one that is annotated, 
while the others are the other parameters. It is important that those parameters are called the 
same in both the modification-function (the lambda in the return-annotation in the example) and 
the annotated function (foo in the example above). The name of the parameter itself in the 
modification-function is irrelevant but should, for readability, usually be the same as the parameter
that is annotated by this modification-function.
    
For example, the following works:
    
```python
from typing_exe.annotations import Modify


def foo(a, b: Modify[lambda whatever, a: whatever + a]):
    ...
```
        
But this doesn't:
    
```python
from typing_exe.annotations import Modify


def foo(a, b: Modify[lambda b, whatever: b + whatever]):
    ...
```
    
Good form would be the following:
    
```python
from typing_exe.annotations import Modify


def foo(a, b: Modify[lambda b, a: b + a]):
     ...
```
        
Of course, the modification-functions don't have to be lambdas. 

    
    