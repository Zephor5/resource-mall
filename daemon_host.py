# coding=utf-8
# eric_wu<zephor@qq.com>
import argparse
import thread
import threading
import time

import docker
from docker.errors import APIError
from flask import Flask, request
from requests import ConnectionError

import utils.system as cs
from configs import cfg
from consts import CONFIG_SEP
from models.host import Host
from modules.allocator_mysql import AllocatorMysql
from modules.server_builder_base import ServerBuilderBase
from utils.errors import AllocatorError
from utils.log import get_logger

logger = get_logger(__file__)


def init(args):
    import logging
    from mongoengine import connect

    cfg.bootstrap(args.env)
    logging.basicConfig(
        level=cfg.log.level,
        format=cfg.log.format
    )

    # init db connection fixme more args
    connect(host=cfg.mongo.host, db=cfg.mongo.db)


def env_prepare():
    """test for resource host env requirements
    :return is_ok(boolean) flag
    """

    # prepare directory
    data_path = cfg.sys.data_path
    if not cs.ensure_dir_access(data_path):
        logger.fatal('access check fail for "%s", '
                     'pls ensure read and write access to an existing dir' % data_path)
        return False

    if not cs.ensure_unique(data_path):
        logger.fatal('host daemon process already running')
        return False

    # check docker
    docker_client = docker.from_env()
    try:
        docker_client.images.list()
    except (ConnectionError, APIError):
        logger.fatal('pls ensure docker server running healthily on this host')
        return False

    # prepare docker images
    for resource_name in cfg.sys.resources.split(CONFIG_SEP):
        res_conf = getattr(cfg, resource_name)
        for version in res_conf.versions.split(CONFIG_SEP):
            docker_client.images.pull(resource_name, version)
            logger.info('pulling docker image: %s(%s)' % (resource_name, version))
    return True


def keep_alive(host_obj, interval=30):
    def _heartbeat():
        dur = 0
        while 1:
            try:
                time.sleep(interval - dur)
                start = time.time()
                info = cs.collect_running_info(cfg.sys.data_path)
                host_obj.heartbeat(**info)
                logger.info('beat...')
                dur = time.time() - start
            except Exception as e:
                logger.error(e.message)
                logger.error('something happen to heartbeat thread, exit')
                thread.interrupt_main()
                return

    t = threading.Thread(target=_heartbeat)
    t.setDaemon(True)
    t.start()
    logger.info('heartbeat thread started.')


class ServerBuilder(ServerBuilderBase):
    """daemon internal server to receive action requests"""

    @classmethod
    def build(cls):
        app = Flask(__name__)
        cls.register_error(app)
        cls.assemble_routers(app)
        return app

    @classmethod
    def assemble_routers(cls, app):
        def health():
            return 'ok'

        app.route('/health')(health)
        base_url = '/%s/' % cfg.daemon.path_salt + '%s'
        actions = (('create', 'post'), ('delete', 'post'), ('get', 'get'))
        for action, method in actions:
            app.route(
                base_url % action,
                methods=(method,)
            )(getattr(cls, '%s_handler' % action))

    @classmethod
    def get_handler(cls):
        # todo
        pass

    @classmethod
    def create_handler(cls):
        params = request.json
        resource_type = params.pop('resource_type', None)
        host_id = params.pop('host_id')
        # todo param check
        host = Host.objects.get(id=host_id)
        params['host'] = host
        if resource_type == 'mysql':
            try:
                resource = AllocatorMysql.run(**params)
                return cls._format_ret(content=str(resource.id))
            except AllocatorError as e:
                host.recover_port(e.port)
                return cls._format_ret(success=False, error_no=6001, content=e.message)
        elif resource_type == 'redis':
            # todo
            pass

    @classmethod
    def delete_handler(cls):
        pass


def start_serve(ip='0.0.0.0'):
    app = ServerBuilder.build()

    app.run(host=ip, port=cfg.daemon.port, debug=cfg.get_environment() == 'dev')


def main():
    parser = argparse.ArgumentParser(description="host daemon process")
    # env arg, maybe more choices, eg: test, sit
    parser.add_argument('-e', '--env', type=unicode, dest='env', default='dev', help="env type",
                        choices=['dev', 'prod'])

    args = parser.parse_args()

    init(args)

    if not env_prepare():
        return

    info = cs.collect_info(cfg.sys.data_path)
    info.update({'max_instance_num': int(cfg.daemon.max_instance)})

    host = Host.new(**info)

    logger.debug(info)

    # start heartbeat thread
    keep_alive(host, interval=cfg.daemon.interval)

    start_serve(host.ip)


if __name__ == '__main__':
    main()
