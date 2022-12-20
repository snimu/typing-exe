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
        self.hooks = None

    def __getitem__(self, item): ...

    def enforce(self, fct, parameter, parameter_name): ...

    @staticmethod
    def _parse(hooks): ...


class _HooksCreator:
    def __init__(self): ...

    def __getitem__(self, item) -> _Hook: ...


Checks: _ChecksCreator
Hooks: _HooksCreator