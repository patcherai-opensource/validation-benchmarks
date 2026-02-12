import json
import logging
import os
import base64

import tornado.web

from handlers.base import BaseHandler
import config_manager


class CameraHandler(BaseHandler):

    @BaseHandler.auth()
    def get(self, camera_id, op):
        camera_id = int(camera_id)
        camera = config_manager.get_camera(camera_id)
        if not camera:
            self.set_status(404)
            self.write_json({'error': 'Camera not found'})
            return

        if op == 'current':
            self.write_json({
                'id': camera_id,
                'name': camera['name'],
                'status': camera.get('status', 'online'),
                'fps': camera.get('framerate', 15),
                'resolution': camera.get('resolution', '1280x720'),
            })
        elif op == 'snapshot':
            # Return placeholder image data
            self.set_header('Content-Type', 'image/jpeg')
            self.write(b'\xff\xd8\xff\xe0' + b'\x00' * 100)
        else:
            self.set_status(400)
            self.write_json({'error': 'Invalid operation'})
