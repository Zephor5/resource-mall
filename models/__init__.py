# coding=utf-8
# eric_wu<zephor@qq.com>
from mongoengine import signals

from utils.log import get_logger
from .host_event import HostEvent


logger = get_logger(__file__)


def log_host_event(host_cls):
    if signals.signals_available:
        signals.post_save.connect(HostEvent.handle_event, sender=host_cls)
    else:
        logger.warn('host event isn\'t activated because of blinker isn\'t installed')
    return host_cls
