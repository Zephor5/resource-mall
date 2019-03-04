# coding=utf-8
# eric_wu<zephor@qq.com>
from datetime import datetime, timedelta

from mongoengine import Document, StringField, IntField, DateTimeField, Q, DoesNotExist, ListField

from configs import cfg
from consts import HostState
from models import log_host_event
from utils.errors import HostExistsError

_PORT_POOL_N = 10


@log_host_event
class Host(Document):
    """physical node to host resources"""

    meta = {
        'indexes': ['#hostname', '#ip', 'last_beat']
    }

    # basic info
    hostname = StringField(required=True, min_length=8, max_length=128)
    ip = StringField(required=True, regex=r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

    cpu_freq = IntField(required=True)  # Khz
    # min freq among logic cores
    cpu_freq_min = IntField(required=True)  # Khz
    cpu_freq_remain = IntField(required=True)  # Khz

    # total storage size can be used to allocate for resource
    storage_total = IntField(required=True, min_value=100)  # MB
    # free storage size can be used to dispatch actually
    storage_free = IntField(required=True)  # MB
    # remain storage size calculated by dispatch
    storage_remain = IntField(required=True)  # MB

    # total ram size
    mem_total = IntField(required=True, min_value=100)  # MB
    mem_available = IntField(required=True)  # MB
    mem_free = IntField(required=True, )  # MB
    mem_remain = IntField(required=True)  # MB

    # current running number of resource instances
    instance_num = IntField(required=True, default=0)
    # number remain after pre-alloc
    instance_remain = IntField(required=True)
    # max available instance number
    max_instance_num = IntField(required=True, min_value=1)

    # ports pool, a port will be put back here in case being deleted
    ports = ListField(IntField())
    next_port = IntField(required=True)

    # state fields
    state = IntField(required=True, choices=HostState.all)
    last_beat = DateTimeField(required=True, default=datetime.utcnow)
    created_at = DateTimeField(required=True, default=datetime.utcnow)

    @classmethod
    def new(cls, **kwargs):
        hostname = kwargs.get('hostname', '')
        ip = kwargs.get('ip', '')
        try:
            host = cls.objects.filter(Q(hostname=hostname) or Q(ip=ip)).get()
        except DoesNotExist:
            host = None
        if host is None:
            host = cls(**kwargs)
            host.cpu_freq_remain = host.cpu_freq
            host.mem_remain = host.mem_available
            host.storage_remain = host.storage_free
            host.instance_remain = host.max_instance_num

            # get config
            port_start, port_end = cfg.daemon.service_ports.split('-')
            port_start = int(port_start)
            port_end = int(port_end) + 1

            if host.max_instance_num > (port_end - port_start):
                raise SystemError('port resource can\'t meet the instance num')

            host.ports.extend(range(port_start, min(port_end, port_start + _PORT_POOL_N)))
            host.next_port = host.ports[-1] + 1
        # fixme this is disabled for dev purpose
        # elif host.state != HostState.REMOVED:
        #     raise HostExistsError('host %s<%s> already exists' % (hostname, ip))
        host.state = HostState.ALIVE
        host.last_beat = datetime.utcnow()
        return host.save()

    @classmethod
    def generate_port(cls, ip):
        """generate an available port for the host"""
        try:
            host = cls.objects(ip=ip).get()
        except DoesNotExist:
            raise RuntimeError('host doesn\'t exist')
        if len(host.ports) == 0:
            _, port_end = cfg.daemon.service_ports.split('-')
            port_end = int(port_end) + 1
            host.ports.extend(range(host.next_port,
                                    min(port_end, host.next_port + _PORT_POOL_N)))
            if len(host.ports) == 0:
                raise RuntimeError('run out of port')

            host.next_port = host.ports[-1] + 1

        port = host.ports.pop()
        host.save()
        return port

    @classmethod
    def get_available_host(cls, cpu_freq, mem_size, storage_size):
        """get an available host to setup the requested resource
        todo there should be a properer way in distributed case"""
        t = datetime.utcnow() - timedelta(seconds=cfg.daemon.interval * 3)
        try:
            host = cls.objects(
                state=HostState.ALIVE,
                cpu_freq_remain__gt=cpu_freq,
                mem_remain__gt=mem_size,
                storage_remain__gt=storage_size,
                instance_remain__gt=0,
                last_beat__gt=t
            ).get()
        except DoesNotExist:
            return
        host.cpu_freq_remain -= cpu_freq
        host.mem_remain -= mem_size
        host.storage_remain -= storage_size
        host.instance_remain -= 1
        host.save()
        return host

    def recover_port(self, port):
        if port is not None:
            self.ports.append(port)
            self.save()
        return self

    @classmethod
    def recover(cls, host_id, cpu_freq, mem_size, storage_size, port=None):
        """used for recovery in case allocated but creation fail"""
        host = cls.objects.get(id=host_id)
        host.cpu_freq_remain += cpu_freq
        host.mem_remain += mem_size
        host.storage_remain += storage_size
        host.instance_remain += 1
        if port is not None:
            host.ports.append(port)
        return host.save()

    @classmethod
    def recover_from_resource(cls, resource):
        """used for release infra resource when instance resource is deleted"""
        return cls.recover(
            resource.host_id,
            resource.cpu_freq,
            resource.mem_size,
            resource.storage_size,
            resource.port
        )

    def heartbeat(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        if self.storage_free < cfg.daemon.min_require_storage_size:
            self.state = HostState.FULL
        self.last_beat = datetime.utcnow()
        return self.save()
