import typing_exe as texe


def test_is_typehint():
    assert not texe.annotations.is_typehint(None)
