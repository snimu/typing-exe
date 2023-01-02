# ParameterData

A `dataclass` that holds information about a function that is annotated by 
[@execute_annotations](https://snimu.github.io/typing-exe/execute_annotations/).

It is recommended that users don't use this class directly. However, a short description of its 
members is provided below anyways.


## `ParameterData`

- `function_signature: inspect.Signature` The signature of the function 
- `arg_annotations: dict` A dictionary in the form `{parameter-index: annotation}`. Only includes annotations from 
the `typing-exe`-package
- `argname_from_index: dict` A dictionary in the form `{parameter-index: parameter-name}`
- `index_from_argname: dict` A dictinary in the form `{parameter-name: parameter-index}`
- `kwarg_annotations: dict` A dictionary in the form `{parameter-name: annotation}`. Only includes annotations from
the `typing-exe`-package
- `defaultdata: dict` A dictionary in the form `{parameter-name: {"index": parameter-index, "value": parameter-value}}`
