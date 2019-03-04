# coding=utf-8
# eric_wu<zephor@qq.com>
import os.path as op

from utils.python import EnumTypeMeta

__all__ = ['PATH_ROOT', 'PATH_CONFIGS', 'PATH_TEMPLATES', 'CONFIG_SEP', 'HostState']

# global paths
PATH_ROOT = op.abspath(op.join(op.dirname(__file__), '..'))

PATH_CONFIGS = op.join(PATH_ROOT, 'configs')

PATH_TEMPLATES = op.join(PATH_ROOT, 'templates')

CONFIG_SEP = ','


# state enums
class HostState(object):
    __metaclass__ = EnumTypeMeta

    REMOVED = -1
    UNREACHABLE = 0
    ALIVE = 1
    FULL = 2


if __name__ == '__main__':
    print PATH_ROOT
    print PATH_CONFIGS
    print HostState.options
