import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, 'storage', 'easyappointments.db')
SECRET_KEY = secrets.token_hex(32)

# Application settings
APP_NAME = 'Easy!Appointments'
APP_VERSION = '1.4.3'

# Admin credentials (set during installation)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

# Email notification settings
SMTP_HOST = 'localhost'
SMTP_PORT = 25
NOTIFICATIONS_ENABLED = False

# Google Analytics
GOOGLE_ANALYTICS_CODE = ''

# Matomo Analytics  
MATOMO_ANALYTICS_URL = ''
