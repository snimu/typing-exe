class _Checks:
    def __init__(self):
        self.typehint = None
        self.checks = None

    def __getitem__(self, checks):
        self.typehint, self.checks = self._parse(checks)
        return self

    def enforce(self, fct, ):

    @staticmethod
    def _parse(checks):
        # Checks is never empty because this eventuality
        #   is caught by _ChecksCreator
        if not isinstance(checks, tuple):
            checks = (checks, )
        if len(checks) == 1 and type(checks[0]) is type:
            return checks[0], None
        if len(checks) == 1 and callable(checks[0]):
            return None, checks
        if len(checks) > 1:
            typehint = None
            if type(checks[0]) is type:
                typehint = checks[0]
                checks = checks[1:]

            checks = [check for check in checks if callable(check)]
            checks = None if not checks else checks
            return typehint, checks

        return None, None   # in case of complete nonsense


class _Hook:
    def __init__(self):
        self.check = None
        self.hook = None
        self.description = None

    def __getitem__(self, checks):
        self.check = checks[0]
        self.hook = checks[1]
        self.description = checks[2] if len(checks) == 3 else None
        return self


class _ChecksCreator:
    def __init__(self):
        self.typehint = None
        self.checks = None

    def __getitem__(self, item):
        return _Checks()[item]


class _HookCreator:
    def __init__(self):
        self.check = None
        self.hook = None
        self.description = None

    def __getitem__(self, item):
        return _Hook()[item]


Checks = _ChecksCreator()
Checks.__doc__ = \
    """TODO"""

Hook = _HookCreator()
Hook.__doc__ = \
    """TODO"""
