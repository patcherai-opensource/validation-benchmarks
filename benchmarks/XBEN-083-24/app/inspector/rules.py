"""Introspection rules management."""

import logging
import uuid as uuid_lib

from sqlalchemy import text

from inspector import db

LOG = logging.getLogger(__name__)


def get_all_rules():
    """Get all introspection rules."""
    session = db.get_session()
    rows = session.execute(text("SELECT * FROM rules ORDER BY created_at")).fetchall()
    return [dict(r._mapping) for r in rows]


def get_rule(rule_uuid):
    """Get a single rule by UUID."""
    session = db.get_session()
    result = session.execute(
        text("SELECT * FROM rules WHERE uuid = :uuid"),
        {"uuid": rule_uuid}
    ).fetchone()
    if not result:
        raise RuleNotFoundError("Rule %s not found" % rule_uuid)
    return dict(result._mapping)


def delete_rule(rule_uuid):
    """Delete a rule by UUID."""
    session = db.get_session()
    result = session.execute(
        text("DELETE FROM rules WHERE uuid = :uuid"),
        {"uuid": rule_uuid}
    )
    session.commit()
    if result.rowcount == 0:
        raise RuleNotFoundError("Rule %s not found" % rule_uuid)


class RuleNotFoundError(Exception):
    pass
