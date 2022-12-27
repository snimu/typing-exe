import inspect
from typing import Union, Type, Any
from collections import OrderedDict

import typing_exe as texe
from typing_exe.early_return import EarlyReturn


class _PreProcess:
    @staticmethod
    def parse_getitem(items):
        # Checks is never empty because this eventuality
        #   is caught by _HintsCreator
        if not isinstance(items, tuple):
            items = (items,)
        if len(items) == 1 and texe.util.is_typehint(items[0]):
            return items[0], None
        if len(items) == 1 and callable(items[0]):
            return None, {items[0]: inspect.signature(items[0])}
        if len(items) > 1:
            typehint = None
            if texe.util.is_typehint(items[0]):
                typehint = items[0]
                items = items[1:]

            new_items = OrderedDict()
            for item in items:
                if callable(item) and not texe.util.is_typehint(item):
                    new_items[item] = inspect.signature(item)
            items = new_items
            items = None if not items else items   # Assume None or has entries in .enforce
            return typehint, items

        return None, None  # in case of complete nonsense

    @staticmethod
    def execute_item(item: callable, signature: inspect.Signature, parameter: Any) -> Any:
        return item(parameter)


class _Assert(_PreProcess):
    def __getitem__(self, items):
        self.typehint, self.items = self.parse_getitem(items)
        return self

    def enforce(self, fct, parameter, parameter_name):
        if self.items is None or parameter is None:
            return

        for item, signature in self.items.items():
            if not self.execute_item(item, signature, parameter):
                err_str = f"\nCheck failed! \n" \
                          f"\t- Callable: \n" \
                          f"\t\t- Name: {fct.__qualname__}\n" \
                          f"\t\t- Module: {fct.__module__}\n" \
                          f"\tAssertion:\n" \
                          f"\t\t- Name: {item.__qualname__}\n" \
                          f"\t\t- Module: {item.__module__}\n" \
                          f"\t- Parameter: \n" \
                          f"\t\t- Name: {parameter_name}\n" \
                          f"\t\t- Value: {parameter}\n"
                raise ValueError(err_str)


class _Modify(_PreProcess):
    def __getitem__(self, items):
        self.typehint, self.items = self.parse_getitem(items)
        return self

    def enforce(self, parameter):
        if self.items is not None:
            for item, signature in self.items.items():
                parameter = self.execute_item(item, signature, parameter)
                if isinstance(parameter, EarlyReturn):
                    return parameter   # Value unpacked in @execute_annotations

        return parameter


class _Sequence:
    def __getitem__(self, items):
        self.typehint, self.items = self.parse(items)
        return self

    def enforce(self, fct, parameter, parameter_name):
        for hint in self.items:
            if isinstance(hint, _Assert):
                hint.enforce(fct, parameter, parameter_name)
            elif isinstance(hint, _Modify):
                parameter = hint.enforce(parameter)
                if isinstance(parameter, EarlyReturn):
                    return parameter   # Value unpacked in @pc.hints.enforce

        return parameter

    def parse(self, items):
        # hints is never empty because this eventuality
        #   is caught by _HintsCreator
        if not isinstance(items, tuple):
            items = (items,)
        if len(items) == 1 and texe.util.is_typehint(items[0]):
            return items[0], None
        if len(items) == 1 and self.is_checks_or_hooks(items[0]):
            return None, items
        if len(items) > 1:
            typehint = None
            if texe.util.is_typehint(items[0]):
                typehint = items[0]
                items = items[1:]

            items = [item for item in items if self.is_checks_or_hooks(item)]
            items = None if not items else items  # Assume None or has entries in .enforce
            return typehint, items

        return None, None  # in case of complete nonsense

    @staticmethod
    def is_checks_or_hooks(item):
        return isinstance(item, _Assert) or isinstance(item, _Modify)


class _HintsCreator:
    def __init__(self, _class: Union[Type[_Assert], Type[_Modify], Type[_Sequence]]):
        self._class = _class

    def __getitem__(self, item) -> Union[_Assert, _Modify]:
        return self._class()[item]

    @property
    def items(self):
        raise AttributeError(
            "'_HintsCreator' object has no attribute 'items'; "
            "Always use 'Assert', 'Modify', and 'Sequence' "
            "with their '__getitem__'-method "
            "('Assert[...]', 'Modify[...]', 'Sequence[...]')"
        )

    @items.setter
    def items(self, item):
        raise AttributeError(
            "'_HintsCreator' object has no attribute 'items'; "
            "Always use 'Assert', 'Modify', and 'Sequence' "
            "with their '__getitem__'-method "
            "('Assert[...]', 'Modify[...]', 'Sequence[...]')"
        )


Assert = _HintsCreator(_Assert)
Assert.__doc__ = \
    """TODO"""

Modify = _HintsCreator(_Modify)
Modify.__doc__ = \
    """TODO"""

Sequence = _HintsCreator(_Sequence)
Sequence.__doc__ = \
    """TODO"""
