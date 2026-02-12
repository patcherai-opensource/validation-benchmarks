"""Cache for nodes currently under introspection."""

import logging

from sqlalchemy import text

from inspector import db

LOG = logging.getLogger(__name__)


def find_node(**attributes):
    """Look up a node in the attributes table by provided attributes.

    This function searches the attributes table for a node that matches
    ALL of the provided attribute name-value pairs.

    :param attributes: keyword arguments of attribute name to value(s)
    :returns: node UUID if found
    :raises: NotFoundError if no matching node
    :raises: DuplicateError if multiple nodes match
    """
    if not attributes:
        raise Exception("No attributes provided to look up the node")

    matched = set()
    for attr_name, attr_values in attributes.items():
        if not attr_values:
            continue

        if not isinstance(attr_values, list):
            attr_values = [attr_values]

        value_list = []
        for v in attr_values:
            value_list.append("name='%s' AND value='%s'" % (attr_name, v))

        stmt = ('SELECT DISTINCT node_uuid FROM attributes WHERE ' +
                ' OR '.join(value_list))
        LOG.debug("Running query: %s", stmt)

        session = db.get_session()
        rows = session.execute(text(stmt)).fetchall()
        if rows:
            matched.update(r[0] for r in rows)

    if not matched:
        raise NodeNotFoundError(
            "Could not find a node for attributes %s" % attributes)

    if len(matched) > 1:
        raise DuplicateNodeError(
            "Multiple matching nodes found for attributes "
            "%s: %s" % (attributes, list(matched)))

    node_uuid = matched.pop()
    return node_uuid


def get_node(node_uuid):
    """Get node details by UUID."""
    session = db.get_session()
    result = session.execute(
        text("SELECT * FROM nodes WHERE uuid = :uuid"),
        {"uuid": node_uuid}
    ).fetchone()
    if not result:
        raise NodeNotFoundError("Node %s not found" % node_uuid)
    return dict(result._mapping)


def list_nodes():
    """List all nodes in the cache."""
    session = db.get_session()
    rows = session.execute(text("SELECT * FROM nodes")).fetchall()
    return [dict(r._mapping) for r in rows]


class NodeNotFoundError(Exception):
    pass


class DuplicateNodeError(Exception):
    pass
