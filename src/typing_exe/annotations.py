from typing import Union, Type

import typing_exe as texe
from typing_exe.early_return import EarlyReturn


def parse(values):
    # Checks is never empty because this eventuality
    #   is caught by _HintsCreator
    if not isinstance(values, tuple):
        values = (values,)
    if len(values) == 1 and texe.util.is_typehint(values[0]):
        return values[0], None
    if len(values) == 1 and callable(values[0]):
        return None, values
    if len(values) > 1:
        typehint = None
        if texe.util.is_typehint(values[0]):
            typehint = values[0]
            values = values[1:]

        values = [value for value in values if callable(value) and not texe.util.is_typehint(value)]
        values = None if not values else values   # Assume None or has entries in .enforce
        return typehint, values

    return None, None  # in case of complete nonsense


class _Assert:
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


class _Modify:
    def __init__(self):
        self.typehint = None
        self.hooks = None

    def __getitem__(self, hooks):
        self.typehint, self.hooks = parse(hooks)
        return self

    def enforce(self, parameter):
        if self.hooks is not None:
            for hook in self.hooks:
                parameter = hook(parameter)
                if isinstance(parameter, EarlyReturn):
                    return parameter   # Value unpacked in @pc.hints.enforce

        return parameter


class _Sequence:
    def __init__(self):
        self.typehint = None
        self.hints = None

    def __getitem__(self, hints):
        self.typehint, self.hints = self.parse(hints)
        return self

    def enforce(self, fct, parameter, parameter_name):
        for hint in self.hints:
            if isinstance(hint, _Assert):
                hint.enforce(fct, parameter, parameter_name)
            elif isinstance(hint, _Modify):
                parameter = hint.enforce(parameter)
                if isinstance(parameter, EarlyReturn):
                    return parameter   # Value unpacked in @pc.hints.enforce

        return parameter

    def parse(self, hints):
        # hints is never empty because this eventuality
        #   is caught by _HintsCreator
        if not isinstance(hints, tuple):
            hints = (hints,)
        if len(hints) == 1 and texe.util.is_typehint(hints[0]):
            return hints[0], None
        if len(hints) == 1 and self.is_checks_or_hooks(hints[0]):
            return None, hints
        if len(hints) > 1:
            typehint = None
            if texe.util.is_typehint(hints[0]):
                typehint = hints[0]
                hints = hints[1:]

            hints = [hint for hint in hints if self.is_checks_or_hooks(hint)]
            hints = None if not hints else hints  # Assume None or has entries in .enforce
            return typehint, hints

        return None, None  # in case of complete nonsense

    @staticmethod
    def is_checks_or_hooks(item):
        return isinstance(item, _Assert) or isinstance(item, _Modify)


class _HintsCreator:
    def __init__(self, _class: Union[Type[_Assert], Type[_Modify], Type[_Sequence]]):
        self._class = _class
        self.typehint = None
        self.checks = None

    def __getitem__(self, item) -> Union[_Assert, _Modify]:
        return self._class()[item]


Checks = _HintsCreator(_Assert)
Checks.__doc__ = \
    """TODO"""

Hooks = _HintsCreator(_Modify)
Hooks.__doc__ = \
    """TODO"""

Sequence = _HintsCreator(_Sequence)
Sequence.__doc__ = \
    """TODO"""
