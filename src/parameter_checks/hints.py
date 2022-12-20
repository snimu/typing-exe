import copy
from functools import wraps
import parameter_checks as pc


def enforce(fct):
    annotations = copy.deepcopy(fct.__annotations__)

    @wraps(fct)
    def _run(*args, **kwargs):
        args = _check_args(fct, args, annotations)
        kwargs = _check_kwargs(fct, kwargs, annotations)
        return fct(*args, **kwargs)

    return _run


def _check_args(fct, args, annotations):
    new_args = []
    for arg, (name, check) in zip(args, annotations.items()):
        if isinstance(check, pc.annotations._Checks):
            check.enforce(fct, arg, name)
            new_args.append(arg)
        elif isinstance(check, pc.annotations._Hooks):
            new_args.append(check.enforce(fct, arg, name))
        else:
            new_args.append(arg)

    return new_args


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


def cleanup(fct):
    pass