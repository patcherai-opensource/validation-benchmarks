import json
import logging
import os

import tornado.web

from handlers.base import BaseHandler
import config_manager
import settings


class ConfigHandler(BaseHandler):

    def get(self, op):
        if op == 'list':
            self.list()
        elif op == 'backup':
            self.backup()
        else:
            self.set_status(400)
            self.write_json({'error': 'Invalid operation'})

    def post(self, op):
        if op == 'add':
            self.add()
        elif op == 'restore':
            self.restore()
        else:
            self.set_status(400)
            self.write_json({'error': 'Invalid operation'})

    @BaseHandler.auth()
    def list(self):
        cameras = config_manager.get_all_cameras()
        main_config = config_manager.get_main_config()
        self.write_json({
            'cameras': cameras,
            'main': main_config
        })

    @BaseHandler.auth(admin=True)
    def backup(self):
        cameras = config_manager.get_all_cameras()
        main_config = config_manager.get_main_config()
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=motioneye-config.tar.gz')
        self.write_json({
            'cameras': cameras,
            'main': main_config
        })

    @BaseHandler.auth(admin=True)
    def add(self):
        try:
            body = json.loads(self.request.body)
        except (json.JSONDecodeError, TypeError):
            self.set_status(400)
            self.write_json({'error': 'Invalid request body'})
            return

        name = body.get('name', 'New Camera')
        proto = body.get('proto', 'mjpeg')
        host = body.get('host', '')
        port = body.get('port', 80)

        camera = config_manager.add_camera(name, proto, host, port)
        self.write_json({'camera': camera})

    @BaseHandler.auth(admin=True)
    def restore(self):
        self.set_status(501)
        self.write_json({'error': 'Not implemented'})
