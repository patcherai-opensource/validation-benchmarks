import json
import os
import logging

import settings

_cameras = {}
_main_config = {}
_next_id = 1


def _load_network_key():
    key_path = os.path.join(settings.DATA_DIR, '.network_key')
    try:
        with open(key_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ''


def init():
    global _cameras, _main_config, _next_id

    primary_key = _load_network_key()

    _main_config = {
        'hostname': 'motioneye-srv01',
        'admin_username': settings.ADMIN_USERNAME,
        'normal_username': 'user',
        'show_advanced': True,
        'motion_binary': '/usr/bin/motion',
        'wpa_supplicant': False,
        'timezone': 'UTC',
        'log_level': 'info',
        'listen_port': 5003,
        'storage_path': '/data/media',
    }

    _cameras = {
        1: {
            'id': 1,
            'name': 'Front Door',
            'enabled': True,
            'proto': 'mjpeg',
            'host': '192.168.1.101',
            'port': 8080,
            'path': '/video',
            'resolution': '1920x1080',
            'framerate': 25,
            'rotation': 0,
            'auth_mode': 'basic',
            'stream_auth_mode': 'basic',
            'camera_username': 'admin',
            'camera_password': 'cam_front_2024',
            'network_key': primary_key,
            'storage_device': 'local-disk',
            'upload_enabled': False,
            'upload_server': '',
            'upload_location': '',
            'upload_username': '',
            'upload_password': '',
            'text_overlay': True,
            'motion_detection': True,
            'motion_threshold': 1500,
            'status': 'online',
        },
        2: {
            'id': 2,
            'name': 'Backyard',
            'enabled': True,
            'proto': 'rtsp',
            'host': '192.168.1.102',
            'port': 554,
            'path': '/stream1',
            'resolution': '1280x720',
            'framerate': 15,
            'rotation': 0,
            'auth_mode': 'digest',
            'stream_auth_mode': 'digest',
            'camera_username': 'viewer',
            'camera_password': 'cam_back_2024',
            'network_key': 'ae47b2c1d9834f01',
            'storage_device': 'local-disk',
            'upload_enabled': True,
            'upload_server': 'ftp://backup.local',
            'upload_location': '/cameras/backyard',
            'upload_username': 'backup',
            'upload_password': 'bkp2024secure',
            'text_overlay': True,
            'motion_detection': True,
            'motion_threshold': 2000,
            'status': 'online',
        },
        3: {
            'id': 3,
            'name': 'Garage',
            'enabled': False,
            'proto': 'mjpeg',
            'host': '192.168.1.103',
            'port': 8080,
            'path': '/mjpeg',
            'resolution': '640x480',
            'framerate': 10,
            'rotation': 180,
            'auth_mode': 'none',
            'stream_auth_mode': 'none',
            'camera_username': '',
            'camera_password': '',
            'network_key': 'f39d0a7e5c1b4820',
            'storage_device': 'network-share',
            'upload_enabled': False,
            'upload_server': '',
            'upload_location': '',
            'upload_username': '',
            'upload_password': '',
            'text_overlay': False,
            'motion_detection': False,
            'motion_threshold': 1500,
            'status': 'offline',
        },
    }
    _next_id = 4


def get_all_cameras():
    return list(_cameras.values())


def get_camera(camera_id):
    return _cameras.get(camera_id)


def get_main_config():
    return _main_config.copy()


def add_camera(name, proto, host, port):
    global _next_id
    camera = {
        'id': _next_id,
        'name': name,
        'enabled': True,
        'proto': proto,
        'host': host,
        'port': port,
        'path': '/',
        'resolution': '1280x720',
        'framerate': 15,
        'rotation': 0,
        'auth_mode': 'none',
        'stream_auth_mode': 'none',
        'camera_username': '',
        'camera_password': '',
        'network_key': '',
        'storage_device': 'local-disk',
        'upload_enabled': False,
        'upload_server': '',
        'upload_location': '',
        'upload_username': '',
        'upload_password': '',
        'text_overlay': True,
        'motion_detection': True,
        'motion_threshold': 1500,
        'status': 'offline',
    }
    _cameras[_next_id] = camera
    _next_id += 1
    return camera


init()
