from typing import Union, Type
import typing


def is_typehint(value) -> bool:
    if type(value) is type:
        return True

    # Can also be from typing module
    name_with_brackets = str(value).split(".")[-1]  # Might be Union or Union[float, int]
    name = name_with_brackets.split("[")[0]  # Now just Union (etc.)
    return name in typing.__all__


def parse(values):
    # Checks is never empty because this eventuality
    #   is caught by _ChecksCreator
    if not isinstance(values, tuple):
        values = (values,)
    if len(values) == 1 and is_typehint(values[0]):
        return values[0], None
    if len(values) == 1 and callable(values[0]):
        return None, values
    if len(values) > 1:
        typehint = None
        if is_typehint(values[0]):
            typehint = values[0]
            values = values[1:]

        values = [value for value in values if callable(value) and not is_typehint(value)]
        values = None if not values else values   # Assume None or has entries in .enforce
        return typehint, values

    return None, None  # in case of complete nonsense


class _Checks:
    def __init__(self):
        self.typehint = None
        self.checks = None

    def __getitem__(self, checks):
        self.typehint, self.checks = parse(checks)
        return self

    def enforce(self, fct, parameter, parameter_name):
        if self.checks is None or parameter is None:
            return

        for check in self.checks:
            if not check(parameter):
                err_str = f"\nCheck failed! \n" \
                          f"\t- Callable: \n" \
                          f"\t\t- Name: {fct.__qualname__}\n" \
                          f"\t\t- Module: {fct.__module__}\n" \
                          f"\t- Parameter: \n" \
                          f"\t\t- Name: {parameter_name}\n" \
                          f"\t\t- Value: {parameter}\n"
                raise ValueError(err_str)


class _Hooks:
    def __init__(self):
        self.typehint = None
        self.hooks = None

    def __getitem__(self, hooks):
        self.typehint, self.hooks = parse(hooks)
        return self

    def enforce(self, fct, parameter, parameter_name):
        if self.hooks is not None:
            for hook in self.hooks:
                parameter = hook(fct, parameter, parameter_name, self.typehint)

        return parameter


class _HintsCreator:
    def __init__(self, _class: Union[Type[_Checks], Type[_Hooks]]):
        self._class = _class
        self.typehint = None
        self.checks = None

    def __getitem__(self, item) -> Union[_Checks, _Hooks]:
        return self._class()[item]


Checks = _HintsCreator(_Checks)
Checks.__doc__ = \
    """TODO"""

Hooks = _HintsCreator(_Hooks)
Hooks.__doc__ = \
    """TODO"""
