# coding=utf-8
# eric_wu<zephor@qq.com>
from mongoengine import Document

from utils.log import get_logger

logger = get_logger(__file__)


class HostEvent(Document):
    # todo log host change event

    @classmethod
    def handle_event(cls, sender, doc, **kwargs):
        logger.debug('post save %s\t\n%s\t\n%s', (sender, doc, kwargs))
