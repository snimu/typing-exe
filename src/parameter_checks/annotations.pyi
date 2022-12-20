class _ChecksCreator:
    def __init__(self):
        self.checks = None
        self.typehint = None

    def __getitem__(self, item): ...


class _HookCreator:
    def __init__(self): ...

    def __getitem__(self, item): ...


Checks: _ChecksCreator
Hook: _HookCreator