"""Processing logic for introspection data."""

import logging

from inspector import node_cache
from inspector import utils

LOG = logging.getLogger(__name__)


def process(introspection_data):
    """Process the introspection data from a ramdisk callback.

    Looks up the node by its attributes (BMC address, MAC addresses),
    validates the data, and updates the node state.

    :param introspection_data: dict containing introspection payload
    :returns: dict with processing result
    """
    try:
        node_uuid = _find_node_info(introspection_data)
    except node_cache.NodeNotFoundError as exc:
        LOG.warning("Node not found: %s", exc)
        return {"error": str(exc)}
    except node_cache.DuplicateNodeError as exc:
        LOG.warning("Duplicate node: %s", exc)
        return {"error": str(exc)}
    except Exception as exc:
        LOG.error("Error looking up node: %s", exc)
        return {"error": str(exc)}

    try:
        node = node_cache.get_node(node_uuid)
    except node_cache.NodeNotFoundError as exc:
        LOG.warning("Node not found in cache: %s", exc)
        return {"error": str(exc)}

    return {
        "uuid": node["uuid"],
        "state": node["state"],
        "manage_boot": bool(node.get("manage_boot", True)),
    }


def _find_node_info(introspection_data):
    """Find node info from introspection data attributes.

    Extracts BMC address and MAC addresses from the introspection
    data and looks up the matching node.
    """
    bmc_address = utils.get_ipmi_address_from_data(introspection_data)
    macs = utils.get_valid_macs(introspection_data)

    return node_cache.find_node(
        bmc_address=bmc_address,
        mac=macs)
