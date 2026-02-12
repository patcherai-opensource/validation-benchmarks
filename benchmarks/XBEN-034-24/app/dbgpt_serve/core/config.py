"""Application configuration."""

import os

# Server settings
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "80"))

# Database settings
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./dbgpt_data.db",
)

# Plugin settings
PLUGINS_DIR = os.environ.get("PLUGINS_DIR", "/app/plugins")
MAX_PLUGIN_SIZE = 50 * 1024 * 1024  # 50MB

# Model settings
DEFAULT_LLM_MODEL = os.environ.get("LLM_MODEL", "chatgpt_proxyllm")
MODEL_SERVER_URL = os.environ.get("MODEL_SERVER", "http://127.0.0.1:8000")

# API settings
API_PREFIX = ""
API_VERSION = "0.7.0"
