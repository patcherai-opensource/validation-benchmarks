from flask import render_template, redirect, url_for, request, session, jsonify
from functools import wraps

from app import app
from app.db import db
from app.models import User, Dashboard, SavedQuery, DatabaseConnection


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        user = User.query.get(session["user_id"])
        if not user or user.role != "Admin":
            return render_template("error.html", message="Forbidden"), 403
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def add_security_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.route("/health")
def health():
    return "OK", 200


@app.route("/", methods=["GET"])
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard_list"))
    return redirect(url_for("login"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard_list"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username, password=password).first()
        if user and user.active:
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            return redirect(url_for("dashboard_list"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/logout/", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard/list/")
@login_required
def dashboard_list():
    user = User.query.get(session["user_id"])
    if user.role == "Admin":
        dashboards = Dashboard.query.all()
    else:
        dashboards = Dashboard.query.filter_by(published=True).all()
    return render_template("dashboard_list.html", dashboards=dashboards, user=user)


@app.route("/dashboard/<int:dashboard_id>/")
@login_required
def dashboard_view(dashboard_id):
    user = User.query.get(session["user_id"])
    dashboard = Dashboard.query.get_or_404(dashboard_id)

    if not dashboard.published and user.role != "Admin":
        return render_template("error.html", message="Dashboard not found"), 404

    return render_template("dashboard_view.html", dashboard=dashboard, user=user)


@app.route("/savedqueryview/list/")
@admin_required
def saved_query_list():
    user = User.query.get(session["user_id"])
    queries = SavedQuery.query.all()
    return render_template("saved_queries.html", queries=queries, user=user)


@app.route("/savedqueryview/<int:query_id>/")
@admin_required
def saved_query_view(query_id):
    user = User.query.get(session["user_id"])
    query = SavedQuery.query.get_or_404(query_id)
    return render_template("saved_query_detail.html", query=query, user=user)


@app.route("/databaseview/list/")
@admin_required
def database_list():
    user = User.query.get(session["user_id"])
    connections = DatabaseConnection.query.all()
    return render_template("databases.html", connections=connections, user=user)


@app.route("/api/v1/me/")
@login_required
def api_me():
    user = User.query.get(session["user_id"])
    return jsonify({
        "result": {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
        }
    })


@app.route("/api/v1/dashboard/")
@login_required
def api_dashboards():
    user = User.query.get(session["user_id"])
    if user.role == "Admin":
        dashboards = Dashboard.query.all()
    else:
        dashboards = Dashboard.query.filter_by(published=True).all()

    result = []
    for d in dashboards:
        result.append({
            "id": d.id,
            "dashboard_title": d.title,
            "slug": d.slug,
            "published": d.published,
        })
    return jsonify({"result": result})


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", message="Page not found"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html", message="Internal server error"), 500
