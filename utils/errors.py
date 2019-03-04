# coding=utf-8
# eric_wu<zephor@qq.com>


class ConfigError(RuntimeError):
    pass


class ConfigNotFoundError(RuntimeError):
    pass


class HostExistsError(RuntimeError):
    pass


class AllocatorError(Exception):
    def __init__(self, message=None, port=None, *args, **kwargs):
        super(AllocatorError, self).__init__(*args, **kwargs)
        self.message = message
        self.port = port  # carry extra info
