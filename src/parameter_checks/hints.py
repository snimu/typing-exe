import copy
import inspect
from functools import wraps

import parameter_checks as pc


def enforce(fct):
    annotations = copy.deepcopy(fct.__annotations__)

    @wraps(fct)
    def _run(*args, **kwargs):
        args = _check_args(fct, args, annotations)
        kwargs = _check_kwargs(fct, kwargs, annotations)
        returns = fct(*args, **kwargs)
        return _check_returns(fct, returns, annotations)

    return _run


def _check_args(fct, args, annotations):

    """
    Run Checks and Hooks on args.

    There is a problem with the simple approach of doing the simple approach of:

        >>> i = 0   # Manual loop because zip and enforce don't work together well
        >>> for arg, (name, check) in zip(args, annotations.items()):
        >>>     if isinstance(check, pc.annotations._Checks):
        >>>         check.enforce(fct, arg, name)
        >>>     elif isinstance(check, pc.annotations._Hooks):
        >>>         args[i] = check.enforce(fct, arg, name)
        >>>     i += 1

    Imagine the following function:

        >>> @pc.hints.enforce
        >>> def foo(a, b: pc.annotations.Checks[lambda b: b != 0]):
        >>>     return a / b

    Now imagine calling it as follows:

        >>> foo(1, 0)

    The loop-approach would assign the annotation of "b" to "a",
      because there is only one annotation and zipping naively
      leads to this alignment of values.
    This means that the Checks wouldn't be enforced on the correct argument.
    Therefore, the args and annotations have to be aligned.
    """
    signature = inspect.signature(fct)
    args = list(args)   # so that Hooks.enforce can overwrite the args
    i = 0   # Manual loop-counter because zip and enumerate don't play together well

    for name, parameter in zip(signature.parameters.keys(), args):
        check = annotations.get(name)
        if isinstance(check, pc.annotations._Checks):
            check.enforce(fct, parameter, name)
        elif isinstance(check, pc.annotations._Hooks):
            args[i] = check.enforce(fct, parameter, name)
        i += 1

    return tuple(args)


def _check_kwargs(fct, kwargs, annotations):
    new_kwargs = {}
    for pname, pvalue in kwargs.items():
        check = annotations.get(pname)
        if isinstance(check, pc.annotations._Checks):
            check.enforce(fct, pvalue, pname)
            new_kwargs[pname] = pvalue
        elif isinstance(annotations.get(pname), pc.annotations._Hooks):
            new_kwargs[pname] = check.enforce(fct, pvalue, pname)
        else:
            new_kwargs[pname] = pvalue

    return new_kwargs


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
