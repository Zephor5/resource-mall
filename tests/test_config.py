# coding=utf-8
# eric_wu<zephor@qq.com>
from configs.config import Config


class TestConfig(object):

    def test_get(self):
        # fixme
        config = Config()
        assert hasattr(config, 'daemon')
        assert config.daemon.port == 10250
