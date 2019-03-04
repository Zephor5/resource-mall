# coding=utf-8
# eric_wu<zephor@qq.com>
import random
import string

from mongoengine import StringField, DoesNotExist

from models.resource_base import ResourceBase


class ResourceMysql(ResourceBase):
    charset = StringField(default='utf8')
    password = StringField(required=True)

    @classmethod
    def new(cls, **kwargs):
        resource = cls()
        for k, v in kwargs.iteritems():
            if hasattr(resource, k):
                setattr(resource, k, v)
        return resource.save()

    @classmethod
    def get_by_id(cls, resource_id):
        try:
            return cls.objects.get(id=resource_id)
        except DoesNotExist:
            return None

    @classmethod
    def generate_password(cls):
        characters = string.ascii_letters + string.punctuation + string.digits
        return "".join(random.choice(characters) for x in range(8))

    def to_json(self):
        data = super(ResourceMysql, self).to_json()
        data.update({
            'charset': self.charset
        })
        return data
