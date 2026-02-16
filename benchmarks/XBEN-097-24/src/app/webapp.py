import os
import time
import threading

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)

from app import __version__
from app.fetcher import retrieve_content
from app.monitor_store import MonitorStore

store = MonitorStore()


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    )

    app.secret_key = os.urandom(32).hex()
    app.config["VERSION"] = __version__

    @app.template_filter("format_ts")
    def _format_timestamp(ts):
        if not ts:
            return "Not yet"
        import datetime
        return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

    # Background worker that processes monitor queue
    worker_thread = threading.Thread(target=_background_worker, args=(app,), daemon=True)
    worker_thread.start()

    @app.after_request
    def strip_server_header(response):
        response.headers.pop("Server", None)
        return response

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("error.html", error_code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("error.html", error_code=500, message="Internal server error"), 500

    @app.route("/")
    def index():
        monitors = store.get_all()
        return render_template(
            "overview.html",
            monitors=monitors,
            version=__version__,
        )

    @app.route("/ping")
    def health_ping():
        return "OK", 200

    @app.route("/settings", methods=["GET"])
    def settings_page():
        return render_template(
            "settings.html",
            version=__version__,
            monitor_count=len(store.get_all()),
            datastore_path=store._datastore_path,
        )

    @app.route("/monitor/add", methods=["POST"])
    def add_monitor():
        target_url = request.form.get("url", "").strip()
        label = request.form.get("label", "").strip()

        if not target_url:
            flash("URL is required.", "error")
            return redirect(url_for("index"))

        # Check for duplicate
        for m in store.get_all():
            if m["url"] == target_url:
                flash("This URL is already being monitored.", "notice")
                return redirect(url_for("index"))

        monitor_id = store.add(url=target_url, label=label)
        flash("Monitor added successfully.")
        return redirect(url_for("index"))

    @app.route("/monitor/<string:monitor_id>/delete", methods=["POST"])
    def delete_monitor(monitor_id):
        if store.delete(monitor_id):
            flash("Monitor removed.")
        else:
            flash("Monitor not found.", "error")
        return redirect(url_for("index"))

    @app.route("/monitor/<string:monitor_id>/check", methods=["POST"])
    def recheck_monitor(monitor_id):
        monitor = store.get(monitor_id)
        if not monitor:
            flash("Monitor not found.", "error")
            return redirect(url_for("index"))

        store.enqueue(monitor_id)
        flash("Recheck queued.")
        return redirect(url_for("index"))

    @app.route("/monitor/<string:monitor_id>/snapshot", methods=["GET"])
    def view_snapshot(monitor_id):
        monitor = store.get(monitor_id)
        if not monitor:
            abort(404)

        return render_template(
            "snapshot.html",
            monitor=monitor,
            version=__version__,
        )

    @app.route("/monitor/<string:monitor_id>/history", methods=["GET"])
    def view_history(monitor_id):
        monitor = store.get(monitor_id)
        if not monitor:
            abort(404)

        return render_template(
            "history.html",
            monitor=monitor,
            version=__version__,
        )

    @app.route("/import", methods=["GET", "POST"])
    def import_page():
        if request.method == "POST":
            urls_text = request.form.get("urls", "")
            count = 0
            for line in urls_text.strip().splitlines():
                line = line.strip()
                if line:
                    store.add(url=line, label="")
                    count += 1
            flash(f"Imported {count} URLs.")
            return redirect(url_for("index"))

        return render_template("import.html", version=__version__)

    return app


def _background_worker(app):
    """Continuously process queued monitor checks."""
    while True:
        try:
            monitor_id = store.dequeue()
            if monitor_id:
                monitor = store.get(monitor_id)
                if monitor:
                    _process_monitor(monitor)
                time.sleep(0.5)
            else:
                time.sleep(1)
        except Exception:
            time.sleep(3)


def _process_monitor(monitor):
    """Fetch content for a monitor and update its snapshot."""
    url = monitor["url"]

    try:
        content, status = retrieve_content(url)
        store.update_snapshot(
            monitor["id"],
            content=content,
            status_code=status,
            error=None,
        )
    except Exception as e:
        store.update_snapshot(
            monitor["id"],
            content=None,
            status_code=0,
            error=str(e),
        )
