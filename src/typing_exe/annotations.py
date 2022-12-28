import inspect
from typing import Union, Type, Any
from collections import OrderedDict

import typing_exe as texe
from typing_exe.early_return import EarlyReturn
from typing_exe.parameter_data import ParameterData


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
    def execute_item(
            context: str,
            item: callable,
            item_signature: inspect.Signature,
            fct,
            parameter: Any,
            parameter_name,
            args,
            kwargs,
            pdata: ParameterData
    ) -> Any:
        if len(item_signature.parameters) == 1:
            return item(parameter)

        # More than one parameter to Assert- or Modify-item -> compare with other parameters
        # Assume that first parameter to item is annotated parameter
        other_parameter_names = list(item_signature.parameters.keys())[1:]
        other_parameters = []
        for idx, pname in enumerate(other_parameter_names):
            if pname in kwargs.keys():
                other_parameters.append(kwargs.get(pname))
            elif pname in pdata.index_from_argname.keys() and pdata.index_from_argname.get(pname) < len(args):
                other_parameters.append(args[pdata.index_from_argname.get(pname)])
            elif pname in pdata.defaultdata.keys():
                other_parameters.append(pdata.defaultdata.get(pname).get("value"))
            else:
                raise ValueError(
                   f"Error with comparing parameters:\n"
                   f"\t- Callable: \n" 
                   f"\t\t- Name: {fct.__qualname__}\n" 
                   f"\t\t- Module: {fct.__module__}\n" 
                   f"\t{context}-statement:\n" 
                   f"\t\t- Name: {item.__qualname__}\n" 
                   f"\t\t- Module: {item.__module__}\n" 
                   f"\t- Annotated parameter: \n" 
                   f"\t\t- Name: {parameter_name}\n" 
                   f"\t\t- Value: {parameter}\n"
                   f"\t- Parameter {idx} to function in {context} has non-existent name:\n"
                   f"\t\t- Name: {pname}"
                )

        return item(parameter, *other_parameters)



class _Assert(_PreProcess):
    def __getitem__(self, items):
        self.typehint, self.items = self.parse_getitem(items)
        return self

    def enforce(self, fct, parameter, parameter_name, args, kwargs, pdata: ParameterData):
        if self.items is None or parameter is None:
            return parameter

        for item, item_signature in self.items.items():
            if not self.execute_item(
                    "Assert", item, item_signature, fct, parameter, parameter_name, args, kwargs, pdata
            ):
                err_str = f"\nAssert failed! \n" \
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

        return parameter


class _Modify(_PreProcess):
    def __getitem__(self, items):
        self.typehint, self.items = self.parse_getitem(items)
        return self

    def enforce(self, fct, parameter, parameter_name, args, kwargs, pdata: ParameterData):
        if self.items is not None:
            for item, signature in self.items.items():
                parameter = self.execute_item(
                    "Modify", item, signature, fct, parameter, parameter_name, args, kwargs, pdata
                )
                if isinstance(parameter, EarlyReturn):
                    return parameter   # Value unpacked in @execute_annotations

        return parameter


class _Sequence:
    def __getitem__(self, items):
        self.typehint, self.items = self.parse(items)
        return self

    def enforce(self, fct, parameter, parameter_name, args, kwargs, pdata: ParameterData):
        for item in self.items:
            parameter = item.enforce(fct, parameter, parameter_name, args, kwargs, pdata)
            if isinstance(parameter, EarlyReturn):
                return parameter   # Value unpacked in @execute_annotations

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
