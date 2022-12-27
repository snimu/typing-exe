import copy
import inspect
from functools import wraps

import typing_exe as texe


def enforce(fct):
    signature = inspect.signature(fct)
    argdata, kwargdata, defaultdata, pnames = _get_data(signature)

    @wraps(fct)
    def _run(*args, **kwargs):
        args = list(args)   # So that they can be changed

        # Defaults
        for pname in defaultdata.keys():
            # Don't touch anything that is in args or kwargs
            if pname in kwargs:
                continue
            if defaultdata.get(pname).get("index") < len(args):   # in args
                continue

            # Handle EarlyReturn
            if isinstance(defaultdata.get(pname).get("annotation"), texe.early_return.EarlyReturn):
                return defaultdata.get(pname).get("annotation").returns

            # If the default-value is not an instance of EarlyReturn,
            #   add it to args or kwargs (depending on what fits better)
            #   to have it checked below
            if signature.parameters.get(pname).kind == inspect.Parameter.POSITIONAL_ONLY:
                args.append(defaultdata.get(pname).get("annotation"))
            else:
                kwargs[pname] = defaultdata.get(pname).get("annotation")

        # Args
        for idx, annotation in argdata.items():
            if idx >= len(args):
                break
            arg = _enforce_annotation(args[idx], pnames[idx], annotation, fct)
            if isinstance(arg, texe.early_return.EarlyReturn):
                return arg.returns
            args[idx] = arg

        # Kwargs
        for pname, parameter in kwargs.items():
            annotation = kwargdata.get(pname)
            if annotation is not None:
                kwarg = _enforce_annotation(parameter, pname, annotation, fct)
                if isinstance(kwarg, texe.early_return.EarlyReturn):
                    return kwarg.returns
                kwargs[pname] = kwarg

        # Return value
        returns = fct(*args, **kwargs)
        if signature.return_annotation != inspect.Parameter.empty \
                and is_package_annotation(signature.return_annotation):
            returns = _enforce_annotation(returns, "return", signature.return_annotation, fct)
            returns = returns.returns if isinstance(returns, texe.early_return.EarlyReturn) else returns

        # Return
        return returns

    return _run


def _get_data(signature):
    argdata = {}
    kwargdata = {}
    defaultdata = {}
    pnames = []

    for i, pname in enumerate(signature.parameters.keys()):
        pnames.append(pname)

        # Always save all defaults for CompareWith
        if signature.parameters.get(pname).default != inspect.Parameter.empty:
            defaultdata[pname] = {
                "index": i,
                "annotation": signature.parameters.get(pname).default
            }

        annotation = signature.parameters.get(pname).annotation

        # Save other data only if it's an annotation
        if not is_package_annotation(annotation):
            continue

        # Save argdata and kwargdata
        if not signature.parameters.get(pname).kind == inspect.Parameter.POSITIONAL_ONLY:
            kwargdata[pname] = annotation

        if not signature.parameters.get(pname).kind == inspect.Parameter.KEYWORD_ONLY:
            argdata[i] = annotation

    return argdata, kwargdata, defaultdata, pnames


def is_package_annotation(annotation):
    annotations = [
        texe.annotations._Checks,
        texe.annotations._Hooks,
        texe.annotations._Sequence
    ]
    return type(annotation) in annotations


def _enforce_annotation(parameter, parameter_name, annotation, fct):
    if isinstance(annotation, texe.annotations._Checks):
        annotation.enforce(fct, parameter, parameter_name)
    elif isinstance(annotation, texe.annotations._Hooks):
        parameter = annotation.enforce(parameter)
        if isinstance(parameter, texe.early_return.EarlyReturn):
            return parameter  # EarlyReturn then handeled in enforce
    elif isinstance(annotation, texe.annotations._Sequence):
        parameter = annotation.enforce(fct, parameter, parameter_name)
        if isinstance(parameter, texe.early_return.EarlyReturn):
            return parameter  # EarlyReturn then handeled in enforce

    return parameter


def cleanup(fct):
    new_annotations = {}

    for parameter, typehint in fct.__annotations__.items():
        if typehint is None:
            continue
        if texe.annotations.is_typehint(typehint):
            new_annotations[parameter] = typehint
        elif is_package_annotation(typehint) \
                and typehint.typehint is not None:   # if it's not None, parse made sure that it's a typehint!
            new_annotations[parameter] = typehint.typehint

    fct.__annotations__ = new_annotations
    return fct