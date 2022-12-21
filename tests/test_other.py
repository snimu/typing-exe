import parameter_checks as pc


def test_is_typehint():
    assert not pc.annotations.is_typehint(None)
