"""Application configuration."""

import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "c9a3f7e2b1d04a8e9f6c5d3e7b2a1f0e"
    )
    MAX_CONTENT_LENGTH = 64 * 1024  # 64KB max request size
    JSON_SORT_KEYS = False
