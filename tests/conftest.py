# coding=utf-8
# eric_wu<zephor@qq.com>
import pytest


def pytest_addoption(parser):
    parser.addoption('--env', type=unicode, dest='env',
                     default='dev', help="env type", choices=['dev', 'prod'])


@pytest.fixture(scope="session", autouse=True)
def bootstrap(request):
    from configs.config import Config
    Config().bootstrap(request.config.getoption('--env'))
