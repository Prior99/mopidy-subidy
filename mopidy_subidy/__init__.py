from __future__ import unicode_literals

import os

from mopidy import ext, config

__version__ = '0.2.1'


class SubidyExtension(ext.Extension):

    dist_name = 'Mopidy-Subidy'
    ext_name = 'subidy'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(SubidyExtension, self).get_config_schema()
        schema['url'] = config.String()
        schema['username'] = config.String()
        schema['password'] = config.Secret()
        return schema

    def setup(self, registry):
        from .backend import SubidyBackend
        registry.add('backend', SubidyBackend)
