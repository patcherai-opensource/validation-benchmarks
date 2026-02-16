import os

DEFAULT_SIGNING_KEY = "insecure-secret-key"


class AppConfig:
    APP_NAME = "DataLens"
    VERSION = "1.8.2"

    SECRET_KEY = os.environ.get("DATALENS_SECRET_KEY", DEFAULT_SIGNING_KEY)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = False

    PREFERRED_URL_SCHEME = "http"
