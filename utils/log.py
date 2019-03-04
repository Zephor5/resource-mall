# coding=utf-8
# eric_wu<zephor@qq.com>
import logging
import os


def get_logger(file_path):
    return logging.getLogger(os.path.splitext(os.path.basename(file_path))[0])
