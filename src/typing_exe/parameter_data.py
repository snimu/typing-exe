import inspect
from dataclasses import dataclass


@dataclass
class ParameterData:
    function_signature: inspect.Signature
    arg_annotations: dict
    argname_from_index: dict
    index_from_argname: dict
    kwarg_annotations: dict
    defaultdata: dict

