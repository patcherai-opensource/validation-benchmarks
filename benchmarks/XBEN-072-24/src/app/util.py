import logging

import netaddr

logger = logging.getLogger(__name__)


def resolve_client_address(request):
    """Determine the remote address of the client.

    Checks for proxy headers to support reverse proxy setups.
    """
    forwarded_for = request.headers.get("X-Forwarded-For", None)
    if forwarded_for is not None:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr


def _parse_trusted_networks(network_list):
    networks = set()
    for entry in network_list:
        try:
            network = netaddr.IPNetwork(entry)
            networks.add(network)
            if network.version == 4:
                networks.add(network.ipv6())
        except Exception:
            logger.warning("Invalid network definition: %s", entry)
    return networks


def check_autologin(request, cfg, user_manager):
    """Check if the request qualifies for automatic local login.

    When localAutologin is enabled and the client address falls within
    one of the configured trusted networks, log in as the configured
    local user automatically.
    """
    ac = cfg.get("accessControl", {})
    if not ac.get("localAutologin", False):
        return None

    autologin_as = ac.get("localAutologinAs")
    trusted_networks_raw = ac.get("trustedNetworks")

    if autologin_as is None or trusted_networks_raw is None:
        return None

    remote_addr = resolve_client_address(request)
    if not remote_addr:
        return None

    trusted_networks = _parse_trusted_networks(trusted_networks_raw)

    try:
        client_ip = netaddr.IPAddress(remote_addr)
        for network in trusted_networks:
            if client_ip in network:
                user = user_manager.find_user(autologin_as)
                if user is not None and user.is_active:
                    return user
    except Exception:
        logger.debug("Could not evaluate autologin for address %s", remote_addr)

    return None