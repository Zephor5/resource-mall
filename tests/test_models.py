# coding=utf-8
# eric_wu<zephor@qq.com>
import pytest
from mongoengine import connect
import mongoengine.connection

from configs import cfg
from models.resource_base import ResourceBase
from models.resource_mysql import ResourceMysql


class TestModels(object):

    @classmethod
    def setup_class(cls):
        connect(host=cfg.mongo.host, db=cfg.mongo.db)

    @classmethod
    def teardown_class(cls):
        mongoengine.connection.disconnect()

    def test_access_generate(self):
        with pytest.raises(RuntimeError) as e:
            ResourceBase.generate_path('1')
            assert e.type is RuntimeError

    def test_generate_path(self):
        assert len(ResourceMysql.generate_path('1')) == 8

    def test_generate_password(self):
        pwd1 = ResourceMysql.generate_password()
        pwd2 = ResourceMysql.generate_password()
        assert isinstance(pwd1, basestring)
        assert pwd1 != pwd2
