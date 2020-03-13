import pathlib

import pkg_resources

from mopidy import config, ext

__version__ = pkg_resources.get_distribution("Mopidy-Subidy").version


class SubidyExtension(ext.Extension):

    dist_name = "Mopidy-Subidy"
    ext_name = "subidy"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
        schema = super().get_config_schema()
        schema["url"] = config.String()
        schema["username"] = config.String()
        schema["password"] = config.Secret()
        schema["legacy_auth"] = config.Boolean(optional=True)
        schema["api_version"] = config.String(optional=True)
        return schema

    def setup(self, registry):
        from .backend import SubidyBackend

        registry.add("backend", SubidyBackend)
