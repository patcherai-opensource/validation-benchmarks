import os
import hashlib

COOKIE_SECRET = 'a8f5f167f44f4964e6c998dee827110c'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'motioneye_admin_2024!'

NORMAL_PASSWORD = ''

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CONF_DIR = os.path.join(DATA_DIR, 'conf')
LOG_DIR = os.path.join(DATA_DIR, 'log')
MEDIA_DIR = os.path.join(DATA_DIR, 'media')

os.makedirs(CONF_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
