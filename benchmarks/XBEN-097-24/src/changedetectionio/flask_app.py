import os
import time
import logging
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort,
)

from changedetectionio import __version__
from changedetectionio.store import ChangeDetectionStore
from changedetectionio.processors import DifferenceDetectionProcessor

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)
app.secret_key = os.environ.get(
    "SECRET_KEY", "t3mps3cretk3y-4-changedetection"
)

datastore = ChangeDetectionStore()
processor = DifferenceDetectionProcessor(datastore)


@app.after_request
def hide_server_info(response):
    response.headers["Server"] = "changedetection.io"
    response.headers.pop("X-Powered-By", None)
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error_code=404, message="Page not found"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html", error_code=500, message="Internal server error"), 500


@app.route("/", methods=["GET"])
def index():
    """Main dashboard listing all watches."""
    watches = datastore.get_all_watches()
    return render_template(
        "index.html",
        watches=watches,
        active_tag=request.args.get("tag", ""),
        version=__version__,
    )


@app.route("/ping", methods=["GET"])
def ping():
    return "OK", 200


@app.route("/form/add/quickwatch", methods=["POST"])
def form_quick_watch_add():
    """Add a new watch via quick-add form."""
    url = request.form.get("url", "").strip()
    tag = request.form.get("tag", "").strip()

    if not url:
        flash("Error: URL field is required.", "error")
        return redirect(url_for("index"))

    watch_uuid = datastore.add_watch(url=url, tag=tag)
    flash("Watch added successfully.", "notice")

    # Trigger an initial check immediately
    try:
        processor.call_browser(watch_uuid)
    except PermissionError as e:
        datastore.update_watch(watch_uuid, {"last_error": str(e)})
        flash("Watch added but initial check failed: {}".format(str(e)), "error")
    except Exception as e:
        datastore.update_watch(watch_uuid, {"last_error": str(e)})

    return redirect(url_for("index"))


@app.route("/edit/<string:uuid>", methods=["GET", "POST"])
def edit_page(uuid):
    """Edit a watch's settings."""
    watch = datastore.get_watch(uuid)
    if not watch:
        abort(404)

    if request.method == "POST":
        new_url = request.form.get("url", "").strip()
        new_tag = request.form.get("tag", "").strip()
        new_title = request.form.get("title", "").strip()

        if new_url:
            datastore.update_watch(uuid, {
                "url": new_url,
                "tag": new_tag,
                "title": new_title,
            })
            flash("Watch updated.", "notice")
        return redirect(url_for("index"))

    return render_template("edit.html", watch=watch, version=__version__)


@app.route("/preview/<string:uuid>", methods=["GET"])
def preview_page(uuid):
    """Show the latest fetched content for a watch."""
    watch = datastore.get_watch(uuid)
    if not watch:
        abort(404)

    content = datastore.get_latest_snapshot(uuid)
    return render_template(
        "preview.html",
        watch=watch,
        content=content,
        version=__version__,
    )


@app.route("/check/<string:uuid>", methods=["GET"])
def trigger_check(uuid):
    """Manually trigger a re-check for a watch."""
    watch = datastore.get_watch(uuid)
    if not watch:
        abort(404)

    try:
        processor.call_browser(uuid)
        flash("Check completed successfully.", "notice")
    except PermissionError as e:
        datastore.update_watch(uuid, {"last_error": str(e)})
        flash("Check failed: {}".format(str(e)), "error")
    except Exception as e:
        datastore.update_watch(uuid, {"last_error": str(e)})
        flash("Check failed: {}".format(str(e)), "error")

    return redirect(url_for("preview_page", uuid=uuid))


@app.route("/delete/<string:uuid>", methods=["GET"])
def delete_page(uuid):
    """Delete a watch."""
    datastore.delete_watch(uuid)
    flash("Watch deleted.", "notice")
    return redirect(url_for("index"))


@app.route("/api/v1/watch", methods=["GET"])
def api_list_watches():
    """API endpoint to list watches."""
    watches = datastore.get_all_watches()
    return jsonify(watches)


@app.route("/api/v1/watch/<string:uuid>", methods=["GET"])
def api_get_watch(uuid):
    """API endpoint to get a single watch."""
    watch = datastore.get_watch(uuid)
    if not watch:
        return jsonify({"error": "Watch not found"}), 404
    return jsonify(watch)


@app.route("/settings", methods=["GET"])
def settings_page():
    """Application settings page."""
    return render_template(
        "settings.html",
        version=__version__,
        allow_file_uri=os.environ.get("ALLOW_FILE_URI", "false"),
        notification_urls=os.environ.get("NOTIFICATION_URLS", ""),
    )


@app.route("/import", methods=["GET", "POST"])
def import_page():
    """Import watches from various formats."""
    if request.method == "POST":
        urls_text = request.form.get("urls", "").strip()
        if urls_text:
            count = 0
            for line in urls_text.split("\n"):
                line = line.strip()
                if line:
                    datastore.add_watch(url=line)
                    count += 1
            flash("Imported {} watches.".format(count), "notice")
        return redirect(url_for("index"))

    return render_template("import.html", version=__version__)
