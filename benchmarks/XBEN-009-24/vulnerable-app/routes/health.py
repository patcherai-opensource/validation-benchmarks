"""Health check endpoints."""

from flask import Blueprint

health_bp = Blueprint("health", __name__)


@health_bp.route("/ping")
def ping():
    return {"status": "ok"}
