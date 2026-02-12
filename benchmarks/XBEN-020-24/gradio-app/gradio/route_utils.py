"""Utility functions for route handling."""

import hashlib
import hmac
import json
from typing import Optional


def strip_url(orig_url: str) -> str:
    """Strip trailing slashes from URL."""
    if orig_url.endswith("/"):
        return orig_url[:-1]
    return orig_url


def get_root_url(
    request_scope: dict,
    route_path: str,
    root_path: Optional[str] = None,
) -> str:
    """Get the root URL for this request."""
    if root_path:
        return strip_url(root_path)
    return ""


def encode_url_or_filename_to_path_safe_name(url_or_filename: str) -> str:
    """Encode a URL or filename to a path-safe name."""
    return hashlib.md5(url_or_filename.encode()).hexdigest()
