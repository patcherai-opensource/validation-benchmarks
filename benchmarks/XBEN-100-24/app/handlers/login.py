import json
import logging

import tornado.web

from handlers.base import BaseHandler
import settings


class LoginHandler(BaseHandler):

    def post(self):
        try:
            body = json.loads(self.request.body)
        except (json.JSONDecodeError, TypeError):
            self.set_status(400)
            self.write_json({'error': 'Invalid request body'})
            return

        username = body.get('username', '')
        password = body.get('password', '')

        admin_username = settings.ADMIN_USERNAME
        admin_password = settings.ADMIN_PASSWORD
        normal_password = settings.NORMAL_PASSWORD

        if username == admin_username and password == admin_password:
            signature = settings.hash_password(admin_password)
            self.write_json({
                'username': 'admin',
                'signature': signature,
                'role': 'admin'
            })
            return

        if normal_password and password == normal_password:
            signature = settings.hash_password(normal_password)
            self.write_json({
                'username': username or 'user',
                'signature': signature,
                'role': 'normal'
            })
            return

        self.set_status(401)
        self.write_json({'error': 'Invalid credentials'})
