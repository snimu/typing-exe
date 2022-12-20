from typing import Union, Type


def is_typehint(value) -> bool: ...


class _Checks:
    def __init__(self):
        self.checks = None
        self.typehint = None

    def __getitem__(self, checks): ...

    def enforce(self): ...


class _Hooks:
    def __init__(self):
        self.typehint = None
        self.hooks = None

    def __getitem__(self, item): ...

    def enforce(self, fct, parameter, parameter_name): ...


class _HintsCreator:
    def __init__(self, _class: Union[Type[_Checks], Type[_Hooks]]):
        self._class = _class
        self.checks = None
        self.typehint = None

    def __getitem__(self, item) -> Union[_Checks, _Hooks]: ...


Checks: _HintsCreator
Hooks: _HintsCreator