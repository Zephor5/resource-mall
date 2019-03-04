# coding=utf-8
# eric_wu<zephor@qq.com>
import os.path as op
import ConfigParser

from consts import PATH_CONFIGS
from utils.errors import ConfigError, ConfigNotFoundError
from utils.python import singleton, UnchangeableBase

__all__ = ['Config']


class ConfigParserProxy(UnchangeableBase):
    """alpha version of `ConfigParser` proxy object"""

    def __init__(self, parser):
        if not isinstance(parser, ConfigParser.ConfigParser):
            raise ConfigError('parser must be an ConfigParser instance')
        self._parser = parser
        self._section = 'DEFAULT'

    def switch(self, sec):
        # todo maybe handled in the future, to change config section at runtime
        pass

    def __getattr__(self, item):
        # todo proxy `ConfigParser` methods
        try:
            val = self._parser.get(self._section, item, raw=True)
        except ConfigParser.NoOptionError:
            return None
        except ConfigParser.NoSectionError:
            raise ConfigNotFoundError('section %s not found' % self._section)

        try:
            # fixme there's potential risk for some config value
            val = int(val)
        except ValueError:
            pass
        return val


@singleton
class Config(UnchangeableBase):
    def __init__(self):
        self._env = None
        self._config_path = None
        self._configs = {}

    def _check(self):
        if self._env is None:
            raise ConfigError('config needs initialization')

    def bootstrap(self, env):
        if self._env is not None:
            return
        self._env = env.lower()
        config_path = op.join(PATH_CONFIGS, env)
        if not op.isdir(config_path):
            raise ConfigError('config path for %s env is not exist' % env)
        self._config_path = config_path
        op.walk(self._config_path, self._load, None)

    def get_environment(self):
        self._check()
        return self._env

    def _load(self, _, base, names):
        for name in names:
            resource = name.rsplit('.', 1)[0]
            if resource == 'bootstrap':
                raise ConfigError('forbidden config name: bootstrap')
            p = ConfigParser.ConfigParser()
            p.read(op.join(base, name))
            self._configs[resource] = ConfigParserProxy(p)

    def __getattr__(self, item):
        self._check()
        try:
            return self._configs[item]
        except KeyError:
            raise ConfigNotFoundError('%s not exist' % item)
