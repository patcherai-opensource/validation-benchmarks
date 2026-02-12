"""Web UI routes for the prompt service."""

from flask import Blueprint, render_template

ui_bp = Blueprint("ui", __name__)


@ui_bp.route("/")
def index():
    return render_template("index.html")


@ui_bp.route("/docs")
def docs():
    return render_template("docs.html")


@ui_bp.route("/playground")
def playground():
    return render_template("playground.html")
