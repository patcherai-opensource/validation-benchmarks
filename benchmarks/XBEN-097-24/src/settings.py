"""
DataLabel Studio - Configuration Settings
==========================================

This file contains sensitive application configuration.
DO NOT EXPOSE THIS FILE PUBLICLY.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@FLAG@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'datalabel.core',
    'datalabel.projects',
    'datalabel.tasks',
    'datalabel.annotations',
    'datalabel.ml',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'datalabel'),
        'USER': os.environ.get('POSTGRES_USER', 'datalabel'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'datalabel_secret'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_build')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Machine Learning backend configuration
ML_BACKENDS = {
    'default': {
        'url': os.environ.get('ML_BACKEND_URL', 'http://localhost:9090'),
        'timeout': 30,
    }
}

# Export settings
EXPORT_DIR = os.path.join(BASE_DIR, 'export')
EXPORT_FORMATS = ['JSON', 'CSV', 'TSV', 'COCO', 'YOLO']

# Annotation settings
ANNOTATION_OVERLAP = 1
ANNOTATION_SAMPLING = 'random'
