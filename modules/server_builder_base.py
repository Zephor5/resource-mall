# coding=utf-8
# eric_wu<zephor@qq.com>
import json

from flask import jsonify


class BadRequest(Exception):
    def __init__(self, message, error_no=4001):
        self.message = message
        self.error_no = error_no


class ServerBuilderBase(object):
    @classmethod
    def register_error(cls, app):
        app.errorhandler(BadRequest)(cls.error_bad_request)

    @staticmethod
    def error_bad_request(error):
        payload = {
            'success': False,
            'error_no': error.error_no,
            'content': error.message
        }
        return jsonify(payload), 400

    @staticmethod
    def _format_ret(success=True, error_no=None, content=None):
        if isinstance(content, basestring):
            # fixme be more compatible
            try:
                content = json.loads(content)
            except:
                pass
        return jsonify({
            'success': success,
            'error_no': error_no,
            'content': content
        })

    @staticmethod
    def _int_param_check(v, name, base, error_no):
        """check number min base requirement"""
        if v % base != 0:
            raise BadRequest('%s %s must be divisible by %s' % (name, v, base), error_no)
