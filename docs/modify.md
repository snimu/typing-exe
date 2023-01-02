# Modify

Modify your parameters before or your return values after execution of your function-body.
    
## Simple example

Below is a quick example meant to show the How (though maybe not the Why) of using `Modify`.

### The example
    
```python
from typing_exe.annotations import Modify
from typing_exe.decorators import execute_annotations, cleanup_annotations

@cleanup_annotations
@execute_annotations
def foo(
           a: Modify[lambda a: 3 + 2*a + 4*a**2 + a**3], 
           b: Modify[float, lambda b: abs(b)]
) -> Modify[lambda r, a, b: r if a + b > 10_000 else r * 100]:
     return a - b
```

### Explanation

What happens when this function is called? For example, consider calling `foo(2.0, -1.0)`.

1. Before the function body is called, `a` and `b` are modified
    - `a` is given the value 31 according to the equation in its `Modify`-annotation
    - `b` is given the value 1.0
2. The function body is executed
3. The return-value is modified. Since `a + b < 10_000` is `True`, the actual return value of `foo(2.0, -1.0)` 
is `30 * 100 == 3_000`

The modifications are only executed if [@execute_annotations](https://snimu.github.io/typing-exe/execute_annotations/)
is present.

Due to the presence of [@cleanup_annotations](https://snimu.github.io/typing-exe/cleanup_annotations/), 
`foo.__annotations__` will be `{'b': <class 'int'>}`, disregarding the executable annotations.
        
## Description
        
As the two typehints in the example above show, the first entry can either be a typehint, 
or a modification. All other entries are modifications (an arbitrary number of them).

The acceptable forms are:

```python
from typing_exe.annotations import Modify


# 1. typehint and modifications
Modify[<typehint>, <modification1>, <modification2>, ...]

# 2. only modifications
Modify[<modification1>, <modification2>, ...]
```
    
The typehint will be ignored by Modify. Its purpose is twofold: Firstly, it helps readability.
Secondly, when [@execute_annotations](https://snimu.github.io/typing-exe/execute_annotations/)
is paired with [@cleanup_annotations](https://snimu.github.io/typing-exe/cleanup_annotations/), 
only that typehint will be left in the function's annotations, so that the function can be used 
properly by other packages such as [strongtyping](https://github.com/FelixTheC/strongtyping).
    
The modifications are functions that 
take the parameter, modify it, and then return it 
(this only works if your function, `foo` in the example above, is decorated with 
`@execute_annotations`). 
    
It is also possible to make comparisons with other parameters by simply giving your modification-function
more than one parameter, where the first parameter is assumed to be the one that is annotated, 
while the others are the other parameters. It is important that those parameters are called the 
same in both the modification-function (the lambda in the return-annotation in the example) and 
the annotated function (`foo` in the example above). The name of the parameter itself in the 
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

## Larger example

```python
import PIL
import torch 
import torchvision as tv
from typing_exe.annotations import Modify
from typing_exe.decorators import execute_annotations


train_mean = [0.59685254, 0.59685254, 0.59685254]
train_std = [0.16043035, 0.16043035, 0.16043035]


transform_to_tensor = tv.transforms.Compose([
    tv.transforms.ToPILImage(), 
    tv.transforms.ToTensor()
])

normalize = tv.transforms.Normalize(mean=train_mean, std=train_std)

transform_flip = tv.transforms.Compose([
    tv.transforms.RandomHorizontalFlip(),
    tv.transforms.RandomVerticalFlip()
])

transform_colors = tv.transforms.Compose([
    tv.transforms.RandomInvert(),
    tv.transforms.RandomEqualize()
])


# Model1 and Model2 are both used with the same DataLoader the returns PIL.Images
class Model1(torch.nn.Module):
    @execute_annotations
    def forward(self, x: Modify[PIL.Image, transform_to_tensor, normalize]):
        ...
   
   
class Model2(torch.nn.Module):
    @execute_annotations
    def forward(self, x: Modify[PIL.Image, transform_to_tensor, normalize, transform_flip]):
        ...


# Model3 and Model4 use a DataLoader that already returns torch.tensors
class Model3(torch.nn.Module):
    @execute_annotations
    def forward(self, x: Modify[torch.tensor, normalize]):
        ...


class Model4(torch.nn.Module):
    @execute_annotations
    def forward(self, x: Modify[torch.tensor, normalize, transform_colors, transform_flip]):
        ...
```
    