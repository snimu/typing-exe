import typing


def name(value):
    return str(value).split(".")[-1]


print(name(typing.Union[int, float]))
