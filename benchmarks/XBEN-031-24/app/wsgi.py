"""WSGI entry point for salt-api."""

from app import create_app

application = create_app()
