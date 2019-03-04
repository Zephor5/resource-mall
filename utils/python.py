# coding=utf-8
# eric_wu<zephor@qq.com>


class EnumTypeMeta(type):
    """enum type to add extra common properties for enum like objects"""

    def __new__(mcs, cls_name, base_cls, attrs):
        o = type(cls_name, base_cls, attrs)
        enums = {k: v for k, v in attrs.iteritems() if not k.startswith('_') and k.isupper()}
        o.all_names = enums.keys()
        o.all_values = enums.values()
        o.all = o.all_values
        o.options = enums
        return o


def singleton(cls):
    instance = cls()
    if type(instance.__class__) is type:
        instance.__class__.__call__ = lambda self: instance
    else:
        instance.__call__ = lambda: instance
    return instance


class UnchangeableBase(object):
    def __setattr__(self, key, value):
        if key.startswith('_'):
            super(UnchangeableBase, self).__setattr__(key, value)
