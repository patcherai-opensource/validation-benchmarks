import os
import re
import time

# Default settings
ALLOW_FILE_URI = os.environ.get("ALLOW_FILE_URI", "false").lower() == "true"


def is_safe_url(url):
    """Validate that the URL is safe to fetch.
    
    Block file:// protocol access unless explicitly allowed via ALLOW_FILE_URI.
    """
    if not ALLOW_FILE_URI:
        # Check for file protocol - block file:/ URIs
        if re.search(r'^file:/', url.strip(), re.IGNORECASE):
            return False
    return True


class DifferenceDetectionProcessor:
    """Core processor that fetches URL content and detects changes."""

    def __init__(self, datastore):
        self.datastore = datastore

    def call_browser(self, watch_uuid):
        """Fetch the URL for a watch and store the result."""
        watch = self.datastore.get_watch(watch_uuid)
        if not watch:
            raise ValueError("Watch not found: {}".format(watch_uuid))

        url = watch["url"]

        if not is_safe_url(url):
            raise PermissionError(
                "Access denied: file:// protocol is not allowed. "
                "Set ALLOW_FILE_URI=true to enable."
            )

        start_time = time.time()
        content = self._fetch_content(url)
        elapsed = time.time() - start_time

        self.datastore.update_watch(watch_uuid, {
            "fetch_time": round(elapsed, 3),
            "last_error": None,
        })
        self.datastore.save_snapshot(watch_uuid, content)
        return content

    def _fetch_content(self, url):
        """Fetch content from a URL. Supports http(s) and file protocols."""
        stripped = url.strip()

        # Handle file protocol variants
        if stripped.lower().startswith("file://"):
            filepath = stripped[7:]
            return self._read_file(filepath)
        elif stripped.lower().startswith("file:"):
            # Relative or other file: URI format
            filepath = stripped[5:]
            return self._read_file(filepath)

        # Default: HTTP(S) fetch
        import requests
        try:
            resp = requests.get(url, timeout=30, verify=False,
                                headers={"User-Agent": "changedetection.io/{} ".format("0.45.24")})
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException as e:
            raise RuntimeError("Failed to fetch URL: {}".format(str(e)))

    def _read_file(self, filepath):
        """Read a local file and return its content."""
        filepath = os.path.normpath(filepath)
        try:
            with open(filepath, "r") as f:
                return f.read()
        except (IOError, OSError) as e:
            raise RuntimeError("Failed to read file: {}".format(str(e)))
