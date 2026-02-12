"""Utility functions for ironic inspector."""

import re
import logging

LOG = logging.getLogger(__name__)

MAC_REGEX = re.compile(r'^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}$')


def get_ipmi_address_from_data(introspection_data):
    """Extract BMC address from introspection data.

    Looks for BMC address in the inventory section of
    introspection data.

    :param introspection_data: dict with introspection data
    :returns: BMC address string or None
    """
    inventory = introspection_data.get('inventory', {})
    bmc_address = inventory.get('bmc_address')
    if bmc_address:
        LOG.info("Found BMC address: %s", bmc_address)
        return bmc_address

    bmc_address = introspection_data.get('ipmi_address')
    if bmc_address:
        LOG.info("Found IPMI address: %s", bmc_address)
        return bmc_address

    return None


def get_valid_macs(introspection_data):
    """Extract valid MAC addresses from introspection data.

    Searches through interfaces in the inventory to collect
    all valid MAC addresses.

    :param introspection_data: dict with introspection data
    :returns: list of MAC addresses or empty list
    """
    macs = []

    raw_macs = introspection_data.get('macs', [])
    if raw_macs:
        macs.extend(raw_macs)

    inventory = introspection_data.get('inventory', {})
    interfaces = inventory.get('interfaces', [])
    for iface in interfaces:
        mac = iface.get('mac_address')
        if mac:
            macs.append(mac)

    boot_interface = introspection_data.get('boot_interface')
    if boot_interface:
        macs.append(boot_interface)

    return macs
