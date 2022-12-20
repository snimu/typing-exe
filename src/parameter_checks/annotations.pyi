class _Checks:
    def __init__(self):
        self.checks = None
        self.typehint = None

    def __getitem__(self, checks): ...

    @staticmethod
    def _parse(checks): ...

    def enforce(self): ...


class _ChecksCreator:
    def __init__(self):
        self.checks = None
        self.typehint = None

    def __getitem__(self, item) -> _Checks: ...


class _Hook:
    def __init__(self):
        self.check = None
        self.hook = None
        self.description = None

    def __getitem__(self, item): ...


class _HookCreator:
    def __init__(self): ...

    def __getitem__(self, item) -> _Hook: ...


Checks: _ChecksCreator
Hook: _HookCreator