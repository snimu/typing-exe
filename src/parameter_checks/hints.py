import copy
import inspect
from functools import wraps

import parameter_checks as pc


def enforce(fct):
    annotations = copy.deepcopy(fct.__annotations__)

    @wraps(fct)
    def _run(*args, **kwargs):
        args, kwargs = _check_args_kwargs(args, kwargs, fct, annotations)
        returns = fct(*args, **kwargs)
        return _check_returns(fct, returns, annotations)

    return _run


def _check_args_kwargs(args, kwargs, fct, annotations):
    signature = inspect.signature(fct)
    args = list(args)

    for i, name in enumerate(signature.parameters.keys()):
        if i < len(args):
            # Handle positional arguments
            args[i] = _enforce(fct, args[i], name, annotations)
        elif name in kwargs.keys():
            # Handle keyword arguments
            kwargs[name] = _enforce(fct, kwargs[name], name, annotations)
        elif signature.parameters.get(name).default != inspect.Parameter.empty:
            # Handle default arguments that were not explicitly given as args or kwargs
            arg = _enforce(fct, signature.parameters.get(name).default, name, annotations)
            if signature.parameters.get(name).kind == inspect.Parameter.POSITIONAL_ONLY:
                args.append(arg)
            else:
                kwargs[name] = arg

    return tuple(args), kwargs


def _enforce(fct, parameter, name, annotations):
    check = annotations.get(name)
    if isinstance(check, pc.annotations._Checks):
        check.enforce(fct, parameter, name)
    elif isinstance(check, pc.annotations._Hooks):
        parameter = check.enforce(fct, parameter, name)

    return parameter


def _check_returns(fct, returns, annotations):
    if isinstance(annotations.get("return"), pc.annotations._Checks):
        checks = annotations.get("return")
        checks.enforce(fct, returns, "return")
    elif isinstance(annotations.get("return"), pc.annotations._Hooks):
        hooks = annotations.get("return")
        returns = hooks.enforce(fct, returns, "return")
    return returns


def cleanup(fct):
    new_annotations = {}

    for parameter, typehint in fct.__annotations__.items():
        if typehint is None:
            continue
        if pc.annotations.is_typehint(typehint):
            new_annotations[parameter] = typehint
        elif (isinstance(typehint, pc.annotations._Checks) or isinstance(typehint, pc.annotations._Hooks)) \
                and typehint.typehint is not None:   # if it's not None, parse made sure that it's a typehint!
            new_annotations[parameter] = typehint.typehint

    fct.__annotations__ = new_annotations
    return fct
