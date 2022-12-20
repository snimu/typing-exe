class _Checks:
    def __getitem__(self, checks):
        self.checks = self._cleanup(checks)
        return self

    @staticmethod
    def _cleanup(checks):
        return checks


class _Hook:
    def __getitem__(self, checks):
        self.check = checks[0]
        self.hook = checks[1]
        self.description = checks[2] if len(checks) == 3 else None
        return self


class _ItemCreator:
    """
    Given a type in its constructor, _ItemCreator's
    __getitem__ creates a new instance of that type
    and returns the result of that class-instance's
    __getitem__-method on the given inputs.

    This means that it can be used in the following
    way:

     >>> Checks = _ItemCreator(_Checks)
     >>> c = Checks[1, 2, 3]

    Since `Checks` is an instance of `_ItemCreator`,
    this calls `_ItemCreator`'s `__getitem__`-method with (1, 2, 3).
    This method then constructs a `_Checks`-instance and calls its
    `__getitem__`-method with (1, 2, 3), which saves (1, 2, 3) in
    `self.checks` and returns `self`.

    This means that `c` is now an instance of `_Checks` with the
    information given to it saved in that instance.


    The purpose of this is to create an initialization-scheme for
    typechecks that is consistent with normal type-annotation but
    still allows instance-wise data-storage. A decorator has access
    to that data through the `function.__annotations__` of the
    function it decorates.
    """
    def __init__(self, _class):
        self._class = _class

    def __getitem__(self, item):
        return self._class()[item]


Checks = _ItemCreator(_Checks)
Checks.__doc__ = \
    """TODO"""

Hook = _ItemCreator(_Hook)
Hook.__doc__ = \
    """TODO"""


a = Checks[1, 2, 3]
b = Checks[4, 5, 6]

print(a.checks, b.checks)
