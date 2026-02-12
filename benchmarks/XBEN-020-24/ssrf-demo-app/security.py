"""
URL security validation utilities.

Validates URLs to prevent SSRF attacks by checking whether the target
resolves to a private/internal IP address.
"""

import socket
import ipaddress
from urllib.parse import urlparse


def is_private_url(url: str) -> bool:
    """Check if the URL resolves to a private IP address.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL resolves to a private/reserved IP, False otherwise.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname

        if hostname is None:
            return True

        # Resolve hostname to IP
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)

        # Check if the resolved IP is private or reserved
        if ip.is_private or ip.is_reserved or ip.is_loopback or ip.is_link_local:
            return True

        return False
    except (socket.gaierror, ValueError, OSError):
        # If we can't resolve, treat as potentially unsafe
        return True
