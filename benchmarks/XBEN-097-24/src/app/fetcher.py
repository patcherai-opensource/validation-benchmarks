import os
import re
import chardet
import requests

from app.strtobool import strtobool


def _resolve_local_path(uri):
    """Resolve a file protocol URI to a local filesystem path.

    Handles various file URI formats:
      - file:///absolute/path
      - file://localhost/path
      - file:/path
      - file:relative/path (relative to cwd)
    """
    if uri.startswith("file:///"):
        return uri[7:]
    elif uri.startswith("file://localhost/"):
        return uri[16:]
    elif uri.startswith("file://"):
        return uri[7:]
    elif uri.startswith("file:/"):
        return uri[6:]
    elif uri.startswith("file:"):
        # Relative path: file:some/path or file:../path
        return uri[5:].lstrip()
    return None


def retrieve_content(url):
    """Fetch content from a URL and return (text, status_code).

    Supports HTTP/HTTPS via requests library. File protocol access
    is restricted by default for security.
    """

    # Security: block file:// protocol access unless explicitly allowed
    if re.search(r'^file:/', url.strip(), re.IGNORECASE):
        if not strtobool(os.getenv('ALLOW_FILE_URI', 'false')):
            raise PermissionError(
                "file:// type access is denied for security reasons."
            )

    # Handle file protocol URIs that passed security check
    if url.strip().lower().startswith("file:"):
        local_path = _resolve_local_path(url.strip())
        if local_path is not None:
            resolved = os.path.normpath(os.path.join(os.getcwd(), local_path))
            with open(resolved, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            return content, 200

    session = requests.Session()

    timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))

    r = session.request(
        method='GET',
        url=url,
        timeout=timeout,
        verify=False,
    )

    # Detect encoding if not specified in headers
    if not r.headers.get('content-type') or 'charset=' not in r.headers.get('content-type', ''):
        detected = chardet.detect(r.content)
        if detected and detected.get('encoding'):
            r.encoding = detected['encoding']

    if not r.content or not len(r.content):
        raise ValueError(f"Empty response from {url}")

    if r.status_code != 200:
        raise ConnectionError(
            f"Non-200 status code ({r.status_code}) from {url}"
        )

    return r.text, r.status_code
