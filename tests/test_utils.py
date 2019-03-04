# coding=utf-8
# eric_wu<zephor@qq.com>
from configs import cfg
from utils.python import *
from utils.system import *


class TestUtils(object):

    def test_my_enum(self):
        class T(object):
            __metaclass__ = EnumTypeMeta
            A = 1
            B = 2

        assert hasattr(T, 'all')
        assert hasattr(T, 'all_values')
        assert hasattr(T, 'all_names')
        assert hasattr(T, 'options')
        assert len(T.all_values) == 2

    def test_singleton(self):
        @singleton
        class s:
            pass

        @singleton
        class ss(object):
            pass

        assert s() is s()
        assert ss() is ss()

    def test_unchangeable(self):
        class T(UnchangeableBase):
            pass

        t = T()
        t.a = 1
        t._a = 1
        assert not hasattr(t, 'a')
        assert hasattr(t, '_a')
        assert t._a == 1

    def test_get_space(self):
        total = get_space('.', free=False)
        free = get_space('.', free=True)

        assert type(total) == int
        assert total > 0
        assert type(free) == int
        assert free > -1

    def test_system_info(self):
        info = collect_info(cfg.sys.data_path)

        keys = {
            'cpu_freq',
            'cpu_freq_min',
            'mem_total',
            'mem_available',
            'mem_free',
            'storage_total',
            'storage_free'
        }

        for k in keys:
            assert k in info
