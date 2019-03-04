# coding=utf-8
# eric_wu<zephor@qq.com>
import os
from cStringIO import StringIO

from consts.globals import PATH_TEMPLATES


class AllocatorBase(object):
    TEMPLATE_BASE = None
    TEMPLATE_NAME = None

    @classmethod
    def __get_template_content(cls, version):
        if (cls.TEMPLATE_NAME or cls.TEMPLATE_BASE) is None:
            raise ValueError('templates names not defined')
        content = StringIO()
        try:
            f = open(os.path.join(PATH_TEMPLATES, cls.TEMPLATE_NAME % version))
        except IOError:
            f = open(os.path.join(PATH_TEMPLATES, cls.TEMPLATE_BASE))

        for line in f:
            if not line.strip() or line.startswith(';') or line.startswith('#'):
                continue
            content.write(line)

        return content.getvalue()

    @classmethod
    def _write_conf(cls, path, version, **kwargs):
        with open(path, 'w') as f:
            f.write(cls.__get_template_content(version).format(**kwargs))
