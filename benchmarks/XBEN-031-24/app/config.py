"""
Configuration module for the Conductor file distribution service.
"""

import os

# Base directories for managed content distribution
CONTENT_ROOTS = {
    "production": ["/srv/conductor/content/production"],
    "staging": ["/srv/conductor/content/staging"],
    "__env__": ["/srv/conductor/content/__env__"],
}

# Cache settings
CACHE_DIR = "/var/cache/conductor"

# File buffer size for chunked reads (bytes)
FILE_BUFFER_SIZE = 65536

# Ignore patterns for file listings
IGNORED_PATTERNS = [
    "*.pyc",
    "__pycache__",
    ".git",
    ".svn",
]

# Auth configuration
AUTH_TOKEN_EXPIRY = 86400  # seconds

# Server settings
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8080

# Logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING")
LOG_FILE = "/var/log/conductor/conductor.log"
