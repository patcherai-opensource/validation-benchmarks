import functools
import logging
import json

import tornado.web

import settings


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        username = self.get_argument('_username', None)
        signature = self.get_argument('_signature', None)

        admin_username = settings.ADMIN_USERNAME
        admin_password = settings.ADMIN_PASSWORD
        normal_password = settings.NORMAL_PASSWORD

        if username == admin_username and signature:
            expected = settings.hash_password(admin_password)
            if signature == expected:
                return 'admin'

        if username and signature and normal_password:
            expected = settings.hash_password(normal_password)
            if signature == expected:
                return 'normal'

        if not username and not normal_password:
            return 'normal'

        return None

    @staticmethod
    def auth(admin=False):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(handler, *args, **kwargs):
                user = handler.get_current_user()
                if user is None:
                    handler.set_status(401)
                    handler.finish({'error': 'Unauthorized'})
                    return

                if admin and user != 'admin':
                    handler.set_status(403)
                    handler.finish({'error': 'Forbidden'})
                    return

                return func(handler, *args, **kwargs)
            return wrapper
        return decorator

    def write_json(self, data):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        self.finish({'error': 'Internal server error'})
