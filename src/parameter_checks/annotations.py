from typing import Union, Type


class _Parser:
    @staticmethod
    def _parse(inputs):
        # Checks is never empty because this eventuality
        #   is caught by _ChecksCreator
        if not isinstance(inputs, tuple):
            inputs = (inputs,)
        if len(inputs) == 1 and type(inputs[0]) is type:
            return inputs[0], None
        if len(inputs) == 1 and callable(inputs[0]):
            return None, inputs
        if len(inputs) > 1:
            typehint = None
            if type(inputs[0]) is type:
                typehint = inputs[0]
                inputs = inputs[1:]

            inputs = [input for input in inputs if callable(input)]
            inputs = None if not inputs else inputs
            return typehint, inputs

        return None, None  # in case of complete nonsense


class _Checks(_Parser):
    def __init__(self):
        self.typehint = None
        self.checks = None

    def __getitem__(self, checks):
        self.typehint, self.checks = self._parse(checks)
        return self

    def enforce(self, fct, parameter, parameter_name):
        if self.checks is None or parameter is None:
            return

        for check in self.checks:
            if not check(parameter):
                err_str = f"Check failed! \n" \
                          f"\t- function: {fct.__qualname__}\n" \
                          f"\t- parameter: {parameter_name}"
                raise ValueError(err_str)


class _Hooks(_Parser):
    def __init__(self):
        self.typehint = None
        self.hooks = None

    def __getitem__(self, hooks):
        self.typehint, self.hooks = self._parse(hooks)
        return self

    def enforce(self, fct, parameter, parameter_name):
        pass


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
