# coding=utf-8
# eric_wu<zephor@qq.com>
import hashlib
import random
import time
from datetime import datetime

from mongoengine import Document, ObjectIdField, StringField, \
    IntField, DateTimeField, DoesNotExist


class ResourceBase(Document):
    meta = {
        'abstract': True,
        'indexes': ['#host_id', '#container_id', ('ip', 'port'), ('ip', 'data_dir')]
    }

    host_id = ObjectIdField(required=True)
    container_id = StringField(required=True)
    # dynamic physical dir name for this instance
    data_dir = StringField(required=True)
    ip = StringField(required=True)
    port = IntField(required=True)
    cpu_freq = IntField(required=True)
    mem_size = IntField(required=True)
    storage_size = IntField(required=True)

    version = StringField(default='')

    # state todo need state mark
    created_at = DateTimeField(default=datetime.utcnow)

    @classmethod
    def generate_path(cls, ip):
        if cls is ResourceBase:
            raise RuntimeError('forbidden access')

        # fixme risky
        while 1:
            s = "%s:%s:%s" % (ip, time.time(), random.randint(1, 100000))
            path = hashlib.md5(s).hexdigest()[:8]
            try:
                cls.objects(ip=ip, data_dir=path).get()
            except DoesNotExist:
                return path

    def to_json(self):
        return {
            'id': str(self.id),
            'ip': self.ip,
            'port': self.port,
            'cpu_freq': self.cpu_freq,
            'mem_size': self.mem_size,
            'storage_size': self.storage_size,
            'version': self.version,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
