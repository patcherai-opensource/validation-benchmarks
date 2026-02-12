import os
import logging

import tornado.web

from handlers.base import BaseHandler
import settings


class LogHandler(BaseHandler):

    @BaseHandler.auth(admin=True)
    def get(self, name):
        allowed_logs = ['motioneye', 'motion', 'messages']
        if name not in allowed_logs:
            self.set_status(404)
            self.write_json({'error': 'Log not found'})
            return

        log_path = os.path.join(settings.LOG_DIR, name + '.log')
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                content = f.read()
        else:
            content = ''

        self.write_json({'name': name, 'content': content})
