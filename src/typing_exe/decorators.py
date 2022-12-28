import inspect
from functools import wraps

import typing_exe as texe


def execute_annotations(fct):
    signature = inspect.signature(fct)
    argdata, kwargdata, defaultdata, argname_at_index, index_at_argname = _get_data(signature)

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
            if isinstance(defaultdata.get(pname).get("value"), texe.early_return.EarlyReturn):
                return defaultdata.get(pname).get("value").returns

            # If the default-value is not an instance of EarlyReturn,
            #   add it to args or kwargs (depending on what fits better)
            #   to have it checked below
            if signature.parameters.get(pname).kind == inspect.Parameter.POSITIONAL_ONLY:
                args.append(defaultdata.get(pname).get("value"))
            else:
                kwargs[pname] = defaultdata.get(pname).get("value")

        # Args
        for idx, annotation in argdata.items():
            if idx >= len(args):
                break
            arg = annotation.enforce(fct, args[idx], argname_at_index[idx], defaultdata, args, kwargs, index_at_argname)
            if isinstance(arg, texe.early_return.EarlyReturn):
                return arg.returns
            args[idx] = arg

        # Kwargs
        for pname, parameter in kwargs.items():
            annotation = kwargdata.get(pname)
            if annotation is not None:
                kwarg = annotation.enforce(fct, parameter, pname, defaultdata, args, kwargs, index_at_argname)
                if isinstance(kwarg, texe.early_return.EarlyReturn):
                    return kwarg.returns
                kwargs[pname] = kwarg

        # Return value
        returns = fct(*args, **kwargs)
        if signature.return_annotation != inspect.Parameter.empty \
                and texe.util.is_package_annotation(signature.return_annotation):
            returns = signature.return_annotation.enforce(
                fct, returns, "return", defaultdata, args, kwargs, index_at_argname)
            returns = returns.returns if isinstance(returns, texe.early_return.EarlyReturn) else returns

        # Return
        return returns

    return _run


def _get_data(signature):
    argdata = {}
    kwargdata = {}
    defaultdata = {}
    argname_at_index = {}
    index_at_argname = {}

    for i, pname in enumerate(signature.parameters.keys()):
        argname_at_index[i] = pname
        index_at_argname[pname] = i

        # Always save all defaults for CompareWith
        if signature.parameters.get(pname).default != inspect.Parameter.empty:
            defaultdata[pname] = {
                "index": i,
                "value": signature.parameters.get(pname).default
            }

        annotation = signature.parameters.get(pname).annotation

        # Save other data only if it's an annotation
        if not texe.util.is_package_annotation(annotation):
            continue

        # Save argdata and kwargdata
        if not signature.parameters.get(pname).kind == inspect.Parameter.POSITIONAL_ONLY:
            kwargdata[pname] = annotation

        if not signature.parameters.get(pname).kind == inspect.Parameter.KEYWORD_ONLY:
            argdata[i] = annotation

    return argdata, kwargdata, defaultdata, argname_at_index, index_at_argname


def cleanup_annotations(fct):
    new_annotations = {}

    for parameter, typehint in fct.__annotations__.items():
        if typehint is None:
            continue
        if texe.util.is_typehint(typehint):
            new_annotations[parameter] = typehint
        elif texe.util.is_package_annotation(typehint) \
                and typehint.typehint is not None:   # if it's not None, parse made sure that it's a typehint!
            new_annotations[parameter] = typehint.typehint

    fct.__annotations__ = new_annotations
    return fct