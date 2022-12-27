from typing import Union, Type, Any
from typing_extensions import TypeAlias


class _Checks:
    def __init__(self): ...
    def __getitem__(self, checks): ...

    def enforce(self, fct: callable, parameter: Any, parameter_name: str): ...


class _Hooks:
    def __init__(self):
        self.typehint: type
        self.hooks: list

    def __getitem__(self, item): ...

    def enforce(self, fct: callable, parameter: Any, parameter_name: str): ...


class _HintsCreator:
    def __init__(self, _class: Union[Type[_Checks], Type[_Hooks]]): ...
    def __getitem__(self, item) -> Union[_Checks, _Hooks]: ...


Checks: TypeAlias  = _HintsCreator(_Checks)
Hooks: TypeAlias = _HintsCreator(_Hooks)