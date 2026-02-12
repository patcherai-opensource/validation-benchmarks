from flask import Blueprint, render_template, redirect, url_for

views = Blueprint("views", __name__)


@views.route("/")
def index():
    return render_template("index.html")


@views.route("/login")
def login_page():
    return render_template("login.html")


@views.route("/swagger/v1")
def swagger():
    return render_template("swagger.html")


@views.route("/health")
def health():
    return "OK", 200
