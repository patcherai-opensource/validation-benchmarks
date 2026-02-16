"""Utility helpers for the ModelHub Serve application."""

from __future__ import annotations

import httpx


def strip_trailing_path(orig_url: str) -> str:
    """Strip query parameters and trailing slash from a URL string."""
    parsed = httpx.URL(orig_url)
    stripped = parsed.copy_with(query=None)
    return str(stripped).rstrip("/")
