"""
DataAnnotate Platform - Core Settings
=====================================
This file contains sensitive configuration for the data labeling platform.
DO NOT expose this file publicly.
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@FLAG@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dataannotate_db',
        'USER': 'dataannotate',
        'PASSWORD': 'db_password_here',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Storage configuration
DATA_UPLOAD_DIR = '/var/www/app/data/uploads'
EXPORT_DIR = '/var/www/app/data/exports'

# Redis/Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# ML Backend settings
ML_BACKEND_ENABLED = True
ML_BACKEND_URL = 'http://ml-backend:8080'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/dataannotate/app.log',
        },
    },
    'loggers': {
        'dataannotate': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
