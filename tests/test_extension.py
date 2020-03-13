from mopidy_subidy import SubidyExtension


def test_get_default_config():
    ext = SubidyExtension()

    config = ext.get_default_config()

    assert "[subidy]" in config
    assert "enabled = true" in config


def test_get_config_schema():
    ext = SubidyExtension()

    schema = ext.get_config_schema()

    # TODO Test the content of your config schema
    assert "url" in schema
    # assert "password" in schema


# TODO Write more tests
