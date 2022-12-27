import typing
import typing_exe as texe


def is_package_annotation(annotation):
    annotations = [
        texe.annotations._Assert,
        texe.annotations._Modify,
        texe.annotations._Sequence
    ]
    return type(annotation) in annotations


def is_typehint(value) -> bool:
    if type(value) is type:
        return True

    # Can also be from typing module
    name_with_brackets = str(value).split(".")[-1]  # Might be Union or Union[float, int]
    name = name_with_brackets.split("[")[0]  # Now just Union (etc.)
    return name in typing.__all__
