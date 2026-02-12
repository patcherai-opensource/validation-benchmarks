"""Database interface for ironic inspector."""

import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

LOG = logging.getLogger(__name__)

_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        db_host = os.environ.get('DB_HOST', '127.0.0.1')
        db_port = os.environ.get('DB_PORT', '3306')
        db_user = os.environ.get('DB_USER', 'inspector')
        db_password = os.environ.get('DB_PASSWORD', 'inspector_pass')
        db_name = os.environ.get('DB_NAME', 'inspectorDB')

        connection_string = (
            "mysql+pymysql://%s:%s@%s:%s/%s" %
            (db_user, db_password, db_host, db_port, db_name)
        )
        _engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
        )
    return _engine


def get_session():
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = scoped_session(sessionmaker(bind=engine))
    return _session_factory()


def cleanup_session():
    global _session_factory
    if _session_factory is not None:
        _session_factory.remove()
