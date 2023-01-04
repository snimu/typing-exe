# EarlyReturn

Communicate to [Modify](https://snimu.github.io/typing-exe/modify) 
and [Sequence](https://snimu.github.io/typing-exe/sequence) to stop function-execution and return the value given to 
`EarlyReturn`.

Does **not** work for [Assert](https://snimu.github.io/typing-exe/assert).

## Example

### The example

```python
from some_package import load_fct, save_fct
from typing_exe.early_return import EarlyReturn
from typing_exe.annotations import Modify
from typing_exe.decorators import execute_annotations


def load_img(a: str):
    filename = a.split(".")[:-1]
    fileformat = a.split(".")[-1]
    
    if fileformat == "pdf":
        # a was already sharpened and was saved as a pdf-file 
        #   -> sharpen_img should simply return the loaded data
        pdf = load_fct(a)
        return EarlyReturn(pdf)
    
    # Load the image and give it and the filename to sharpen_img
    image = load_fct(a, fileformat=fileformat)
    return filename, image


@execute_annotations
def sharpen_img(a: Modify[str, load_img]):
    filename, image = *a
    # Sharpen the image here 
    image = ... 
    # Save the result
    save_fct(filename + ".pdf", image)
    # Return sharpened image
    return image
```

### Explanation

The function `sharpen_img` is used to load an image from a file given by name. It loads the image
in `load_img`&mdash;executed in `Modify`&mdash;sharpens it, saves it as a PDF-file, and then returns
the sharpened image. 

If the file given to it is already in PDF-format, that means that it has already been
sharpened and so `load_img` loads it and returns an `EarlyReturn` of the loaded, sharpened image. The 
function-body of `sharpen_img` will not be executed; instead, the sharpened image will be returned immediately.


### EarlyReturn for default parameters

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


## `EarlyReturn`

- `returns` The value that should be returned early
