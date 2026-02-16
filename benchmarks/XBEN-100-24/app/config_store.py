import hashlib
import json
import os
import copy
import logging

logger = logging.getLogger('visionguard')

_CONFIG_DIR = os.environ.get('VISIONGUARD_CONF', '/etc/visionguard')
_MAIN_CONFIG_FILE = 'visionguard.json'
_CAMERAS_CONFIG_FILE = 'cameras.json'


class ConfigStore:
    def __init__(self):
        self._main_config = None
        self._cameras = None

    def initialize(self):
        os.makedirs(_CONFIG_DIR, exist_ok=True)
        main_path = os.path.join(_CONFIG_DIR, _MAIN_CONFIG_FILE)
        cameras_path = os.path.join(_CONFIG_DIR, _CAMERAS_CONFIG_FILE)

        if not os.path.exists(main_path):
            default_main = {
                'admin_username': 'admin',
                'admin_password': hashlib.sha1(b'vgadmin2024!').hexdigest(),
                'viewer_username': 'user',
                'viewer_password': '',
                'enabled': True,
                'show_advanced': False,
                'listen_address': '0.0.0.0',
                'port': 5003,
                'motion_detection': True,
                'storage_path': '/var/lib/visionguard/media',
                'log_level': 'info'
            }
            with open(main_path, 'w') as f:
                json.dump(default_main, f, indent=2)

        if not os.path.exists(cameras_path):
            flag_value = self._read_embedded_token()
            default_cameras = [
                {
                    'id': 1,
                    'name': 'Front Entrance',
                    'enabled': True,
                    'type': 'netcam',
                    'url': 'rtsp://192.168.1.101:554/stream1',
                    'username': 'cam_admin',
                    'password': 'cam_pass_101',
                    'resolution': '1920x1080',
                    'framerate': 15,
                    'rotation': 0,
                    'motion_detection': True,
                    'motion_threshold': 1500,
                    'storage_path': '/var/lib/visionguard/media/camera-1',
                    'webhook_url': '',
                    'webhook_token': ''
                },
                {
                    'id': 2,
                    'name': 'Parking Lot',
                    'enabled': True,
                    'type': 'netcam',
                    'url': 'rtsp://192.168.1.102:554/stream1',
                    'username': 'cam_admin',
                    'password': 'cam_pass_102',
                    'resolution': '1280x720',
                    'framerate': 10,
                    'rotation': 0,
                    'motion_detection': True,
                    'motion_threshold': 2000,
                    'storage_path': '/var/lib/visionguard/media/camera-2',
                    'webhook_url': 'https://notify.internal.corp/hooks/parking',
                    'webhook_token': flag_value
                },
                {
                    'id': 3,
                    'name': 'Server Room',
                    'enabled': False,
                    'type': 'v4l2',
                    'device': '/dev/video0',
                    'username': '',
                    'password': '',
                    'resolution': '640x480',
                    'framerate': 5,
                    'rotation': 180,
                    'motion_detection': False,
                    'motion_threshold': 3000,
                    'storage_path': '/var/lib/visionguard/media/camera-3',
                    'webhook_url': '',
                    'webhook_token': ''
                }
            ]
            with open(cameras_path, 'w') as f:
                json.dump(default_cameras, f, indent=2)

        self._load()

    def _read_embedded_token(self):
        token_path = os.path.join(_CONFIG_DIR, '.api_token')
        if os.path.exists(token_path):
            with open(token_path, 'r') as f:
                return f.read().strip()
        return 'TOKEN_NOT_CONFIGURED'

    def _load(self):
        main_path = os.path.join(_CONFIG_DIR, _MAIN_CONFIG_FILE)
        cameras_path = os.path.join(_CONFIG_DIR, _CAMERAS_CONFIG_FILE)

        with open(main_path, 'r') as f:
            self._main_config = json.load(f)

        with open(cameras_path, 'r') as f:
            self._cameras = json.load(f)

    def _save_main(self):
        main_path = os.path.join(_CONFIG_DIR, _MAIN_CONFIG_FILE)
        with open(main_path, 'w') as f:
            json.dump(self._main_config, f, indent=2)

    def _save_cameras(self):
        cameras_path = os.path.join(_CONFIG_DIR, _CAMERAS_CONFIG_FILE)
        with open(cameras_path, 'w') as f:
            json.dump(self._cameras, f, indent=2)

    def get_main(self):
        if self._main_config is None:
            self._load()
        return copy.deepcopy(self._main_config)

    def update_main(self, data):
        for key, value in data.items():
            if key in self._main_config:
                self._main_config[key] = value
        self._save_main()

    def get_cameras(self):
        if self._cameras is None:
            self._load()
        return copy.deepcopy(self._cameras)

    def get_camera(self, camera_id):
        for cam in self._cameras:
            if cam.get('id') == camera_id:
                return copy.deepcopy(cam)
        return None

    def update_camera(self, camera_id, data):
        for i, cam in enumerate(self._cameras):
            if cam.get('id') == camera_id:
                for key, value in data.items():
                    self._cameras[i][key] = value
                self._save_cameras()
                return True
        return False

    def add_camera(self, data):
        max_id = max((c.get('id', 0) for c in self._cameras), default=0)
        data['id'] = max_id + 1
        self._cameras.append(data)
        self._save_cameras()
        return data

    def remove_camera(self, camera_id):
        for i, cam in enumerate(self._cameras):
            if cam.get('id') == camera_id:
                self._cameras.pop(i)
                self._save_cameras()
                return True
        return False
