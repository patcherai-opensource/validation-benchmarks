"""Superset configuration module.

All configuration keys have defaults that are defined in this module.
Users can override these defaults by setting their own values in
superset_config.py or via environment variables.
"""
import os
from datetime import timedelta

# ---------------------------------------------------
# Superset specific config
# ---------------------------------------------------
APP_NAME = "Superset"
APP_ICON = "/static/assets/images/superset-logo-horiz.png"

# Your App secret key. Make sure you override this in your
# superset_config.py. Use a strong complex key. If not overridden,
# Superset will log a warning on startup.
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET")

# The session cookie name
SESSION_COOKIE_NAME = "session"
SESSION_COOKIE_HTTPONLY = True

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True

# Server configuration
SUPERSET_WEBSERVER_ADDRESS = "0.0.0.0"
SUPERSET_WEBSERVER_PORT = 8000
SUPERSET_WEBSERVER_TIMEOUT = 60

ENABLE_PROXY_FIX = False
TALISMAN_ENABLED = False

# Security config
PREVENT_UNSAFE_DB_CONNECTIONS = True
AUTH_TYPE = 1  # Database authentication
AUTH_USER_REGISTRATION = False

# Feature flags
FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "ENABLE_TEMPLATE_PROCESSING": False,
    "ALERT_REPORTS": False,
}

# Cache configuration
CACHE_CONFIG = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
}

# SQL Lab configuration
SQLLAB_TIMEOUT = 30
SQLLAB_DEFAULT_DBID = None
SQL_MAX_ROW = 100000

# CSV export configuration
CSV_EXPORT = {"encoding": "utf-8"}

# Dashboard configuration
DASHBOARD_AUTO_REFRESH_MODE = "force"
DASHBOARD_AUTO_REFRESH_INTERVALS = [
    [0, "Don't refresh"],
    [10, "10 seconds"],
    [30, "30 seconds"],
    [60, "1 minute"],
    [300, "5 minutes"],
    [1800, "30 minutes"],
    [3600, "1 hour"],
    [21600, "6 hours"],
    [43200, "12 hours"],
    [86400, "24 hours"],
]
