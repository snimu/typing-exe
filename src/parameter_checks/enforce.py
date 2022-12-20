import copy
from functools import wraps
import parameter_checks as pc


def checks(fct):
    annotations = copy.deepcopy(fct.__annotations__)

    @wraps(fct)
    def _run(*args, **kwargs):
        for parameter, (name, check) in zip(args, annotations.items()):
            if isinstance(check, pc.annotations._Checks):
                check.enforce(fct, parameter, name)
        for name, parameter in kwargs.items():
            if isinstance(annotations.get(name), pc.annotations._Checks):
                check = annotations.get(name)
                check.enforce(fct, parameter, name)

        return fct(*args, **kwargs)

    return _run


def cleanup(fct):
    pass
