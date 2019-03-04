# coding=utf-8
# eric_wu<zephor@qq.com>
import os

import docker
import requests
from docker.errors import ImageNotFound, APIError

from configs import cfg
from models.host import Host
from models.resource_mysql import ResourceMysql
from modules.allocator_base import AllocatorBase
from utils.errors import AllocatorError
from utils.log import get_logger

logger = get_logger(__file__)


class AllocatorMysql(AllocatorBase):
    # todo config template options aren't optimised
    TEMPLATE_BASE = 'mysql.cnf.tpl'
    TEMPLATE_NAME = 'mysql-%s.cnf.tpl'

    @classmethod
    def run(cls, host, version, charset, engine, cpu_freq, mem_size, storage_size, **kwargs):
        """used by host daemon process to make preparations for running the required resource"""
        port = Host.generate_port(host.ip)
        data_dir_name = ResourceMysql.generate_path(host.ip)
        data_dir_name = 'mysql_%s' % data_dir_name
        data_root = os.path.join(cfg.sys.data_path, data_dir_name)
        conf_dir = os.path.join(data_root, 'conf')
        logs_dir = os.path.join(data_root, 'logs')
        data_dir = os.path.join(data_root, 'data')
        run_dir = os.path.join(data_root, 'run')
        [os.mkdir(p, 0744) for p in (data_root, conf_dir, logs_dir, data_dir, run_dir)]
        cls._write_conf(os.path.join(conf_dir, 'my.cnf'), version, port=port, charset=charset, engine=engine)

        password = ResourceMysql.generate_password()

        docker_client = docker.from_env()
        try:
            container = docker_client.containers.run(
                image='mysql:%s' % version,
                ports={'%s/tcp' % port: port},
                volumes={
                    conf_dir: {'bind': '/etc/mysql', 'mode': 'ro'},
                    logs_dir: {'bind': '/var/log/mysql', 'mode': 'rw'},
                    data_dir: {'bind': '/var/lib/mysql', 'mode': 'rw'},
                    run_dir: {'bind': '/var/run/mysqld', 'mode': 'rw'}
                },
                environment=["MYSQL_ROOT_PASSWORD=%s" % password],
                cpu_period=100000,
                cpu_quota=int((cpu_freq * 1.0 / host.cpu_freq) * 100000),
                mem_limit='%sm' % mem_size,
                # fixme storage control
                # storage_opt={'size': '%sM' % storage_size},
                detach=True
            )
        except (ImageNotFound, APIError) as e:
            logger.error('run docker container failure: %s' % str(e))
            raise AllocatorError(message=str(e), port=port)
        else:
            return ResourceMysql.new(
                host_id=host.id,
                container_id=container.id,
                data_dir=data_dir_name,
                ip=host.ip,
                port=port,
                cpu_freq=cpu_freq,
                mem_size=mem_size,
                storage_size=storage_size,
                version=version,
                charset=charset,
                password=password
            )

    @classmethod
    def alloc(cls, **kwargs):
        cpu_freq = kwargs.get('cpu_freq', 1000)
        mem_size = kwargs.get('mem_size', 100)
        storage_size = kwargs.get('storage_size', 500)
        host = Host.get_available_host(cpu_freq, mem_size, storage_size)
        if host is None:
            return 'no host available'
        url = 'http://%s:%s/%s/create' % (host.ip, cfg.daemon.port, cfg.daemon.path_salt)
        kwargs.update({
            'resource_type': 'mysql',
            'host_id': str(host.id)
        })

        try:
            r = requests.post(url, json=kwargs)
            res = r.json()
        except Exception as e:
            instance = e.message
        else:
            if res['success']:
                instance = ResourceMysql.get_by_id(res['content'])
            else:
                instance = res['content']

        if not isinstance(instance, ResourceMysql):
            Host.recover(host.id, cpu_freq, mem_size, storage_size)
        return instance
