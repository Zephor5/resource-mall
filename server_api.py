# coding=utf-8
# eric_wu<zephor@qq.com>

from flask import Flask, request
from mongoengine import connect

from configs import cfg
from models.resource_mysql import ResourceMysql
from modules.allocator_mysql import AllocatorMysql
from modules.server_builder_base import BadRequest, ServerBuilderBase
from utils.log import get_logger

logger = get_logger(__file__)


class ApiServerBuilder(ServerBuilderBase):
    _setup_ = False

    @classmethod
    def bootstrap(cls, env):
        cfg.bootstrap(env)
        connect(host=cfg.mongo.host, db=cfg.mongo.db)
        cls._setup_ = True

    @classmethod
    def build(cls):
        if cls._setup_ is False:
            logger.error('need setup')
            raise RuntimeError('hasn\'t setup')
        app = Flask(__name__)
        cls.register_error(app)
        cls.assemble_routers(app)
        return app

    @classmethod
    def assemble_routers(cls, app):
        def health():
            return 'ok'

        # todo need to make a customer transformer for ObjectId in route
        # todo and ObjectId is a bit long for url
        app.route('/health')(health)
        app.route('/resource/mysql', methods=('post',))(cls.create_mysql_instance)
        app.route('/resource/mysql/<string(length=24):instance_id>'
                  )(cls.get_mysql_instance)
        app.route('/resource/mysql/<string(length=24):instance_id>',
                  methods=('delete',))(cls.delete_mysql_instance)
        app.route('/resource/redis', methods=('post',))(cls.create_redis_instance)
        app.route('/resource/redis/<string(length=24):instance_id>'
                  )(cls.get_redis_instance)
        app.route('/resource/redis/<string(length=24):instance_id>',
                  methods=('delete',))(cls.delete_redis_instance)

    @classmethod
    def create_mysql_instance(cls):
        version = request.json.get('version', '5.5')
        versions = cfg.mysql.versions.split(',')
        if version not in versions:
            raise BadRequest('version %s not supported' % version, 4001)
        charset = request.json.get('charset', 'utf8')
        try:
            # fixme this is an unreliable way to check charset of mysql
            'a'.encode(charset)
        except LookupError:
            raise BadRequest('charset %s not supported' % charset, 4002)

        engine = request.json.get('engine', 'MYISAM')
        mem_size = int(request.json.get('mem_size', '100'))
        storage_size = int(request.json.get('storage_size', '1000'))
        cpu_freq = int(request.json.get('cpu_freq', '500'))
        for args in ((mem_size, 'mem_size', 10, 4002),
                     (storage_size, 'storage_size', 100, 4003),
                     (cpu_freq, 'cpu_freq', 100, 4004)):
            cls._int_param_check(*args)

        # fixme there need to be a more proper way to pass those growing parameters
        instance = AllocatorMysql.alloc(version=version, charset=charset, engine=engine,
                                        cpu_freq=cpu_freq, mem_size=mem_size, storage_size=storage_size)
        if isinstance(instance, ResourceMysql):
            res = cls._format_ret(content=instance.to_json())
        else:
            res = cls._format_ret(success=False, error_no=5001, content=instance)
        return res

    @classmethod
    def get_mysql_instance(cls, instance_id):
        # todo
        return 'get_mysql_instance, %s' % instance_id

    @classmethod
    def delete_mysql_instance(cls, instance_id):
        # todo
        return 'delete_mysql_instance, %s' % instance_id

    @classmethod
    def create_redis_instance(cls):
        # todo
        return 'create_redis_instance'

    @classmethod
    def get_redis_instance(cls, instance_id):
        # todo
        return 'get_redis_instance, %s' % instance_id

    @classmethod
    def delete_redis_instance(cls, instance_id):
        # todo
        return 'delete_redis_instance, %s' % instance_id


def uwsgi_app():
    """for uwsgi"""
    import os
    ApiServerBuilder.bootstrap(os.environ['ENV'])
    return ApiServerBuilder.build()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='host daemon process')
    # env arg, maybe more choices, eg: test, sit
    parser.add_argument('-e', '--env', type=str, dest='env', default='dev', help='env',
                        choices=['dev', 'prod'])
    parser.add_argument('-p', '--port', type=int, dest='port', default=8888, help='api server port')

    args = parser.parse_args()
    ApiServerBuilder.bootstrap(args.env)
    app = ApiServerBuilder.build()
    app.run(host='0.0.0.0', port=args.port, debug=args.env == 'dev')


if __name__ == '__main__':
    main()
