"""DataHub Workspace Server - File management and workspace API."""
import os
import json
import secrets
import mimetypes
import base64
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Configuration
WORKSPACE_ROOT = os.environ.get("WORKSPACE_ROOT", "/srv/workspace")
SHOW_HIDDEN = os.environ.get("SHOW_HIDDEN", "false").lower() == "true"

# Session management
_active_sessions = {}
SERVER_PID = None

# User accounts (loaded from workspace config)
_users = {
    "admin": {
        "password": "datahub2024",
        "role": "admin",
    },
    "analyst": {
        "password": "workspace",
        "role": "viewer",
    },
}


def _initialize_server():
    """Initialize server state on startup."""
    global SERVER_PID
    SERVER_PID = os.getpid()


def _create_session(username, role):
    """Create a new session and return the token."""
    token = secrets.token_hex(32)
    _active_sessions[token] = {
        "username": username,
        "role": role,
        "created": datetime.now(timezone.utc).isoformat(),
    }
    return token


def _is_hidden(path, root_dir):
    """Check if the given path or any of its ancestors (up to root_dir) is hidden.

    A file or directory is considered hidden if its name starts with a dot.
    """
    abs_path = os.path.abspath(path)
    abs_root = os.path.abspath(root_dir)

    current = abs_path
    while current != abs_root and current != os.path.dirname(current):
        basename = os.path.basename(current)
        if basename.startswith("."):
            return True
        current = os.path.dirname(current)

    return False


def _get_os_path(api_path):
    """Convert API path to OS path."""
    api_path = api_path.strip("/")
    safe_path = os.path.normpath(api_path)
    if safe_path.startswith("..") or "/../" in safe_path:
        return None
    os_path = os.path.join(WORKSPACE_ROOT, safe_path)
    if not os.path.abspath(os_path).startswith(os.path.abspath(WORKSPACE_ROOT)):
        return None
    return os_path


def require_auth(f):
    """Decorator to require a valid session token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get("token")
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("token "):
                token = auth_header[6:]
        if not token or token not in _active_sessions:
            return jsonify({"message": "Authentication required. Provide a valid session token."}), 403
        return f(*args, **kwargs)
    return decorated


def _base_model(api_path, os_path):
    """Build the base model for a file or directory."""
    try:
        info = os.stat(os_path)
    except OSError:
        return None

    model = {
        "name": os.path.basename(api_path) or "/",
        "path": api_path,
        "last_modified": datetime.fromtimestamp(info.st_mtime, tz=timezone.utc).isoformat(),
        "created": datetime.fromtimestamp(info.st_ctime, tz=timezone.utc).isoformat(),
        "content": None,
        "format": None,
        "mimetype": None,
        "size": info.st_size if not os.path.isdir(os_path) else None,
        "writable": os.access(os_path, os.W_OK),
    }
    return model


def _dir_model(api_path, os_path, content=True):
    """Build a model for a directory.

    When listing directory contents, hidden files/dirs are filtered out
    if SHOW_HIDDEN is False. Access to hidden directories themselves is
    also blocked to prevent enumeration.
    """
    if not os.path.isdir(os_path):
        return None

    if _is_hidden(os_path, WORKSPACE_ROOT) and not SHOW_HIDDEN:
        return None

    model = _base_model(api_path, os_path)
    if model is None:
        return None
    model["type"] = "directory"

    if content:
        contents = []
        try:
            entries = sorted(os.listdir(os_path))
        except OSError:
            entries = []

        for name in entries:
            entry_os_path = os.path.join(os_path, name)
            entry_api_path = f"{api_path}/{name}".strip("/")

            if not SHOW_HIDDEN and name.startswith("."):
                continue

            try:
                os.stat(entry_os_path)
            except OSError:
                continue

            if os.path.isdir(entry_os_path):
                entry = _base_model(entry_api_path, entry_os_path)
                if entry:
                    entry["type"] = "directory"
                    contents.append(entry)
            elif os.path.isfile(entry_os_path):
                entry = _base_model(entry_api_path, entry_os_path)
                if entry:
                    entry["type"] = "file"
                    entry["mimetype"] = mimetypes.guess_type(entry_os_path)[0]
                    contents.append(entry)

        model["content"] = contents
        model["format"] = "json"

    return model


def _file_model(api_path, os_path, content=True, fmt=None):
    """Build a model for a file.

    Returns file metadata and optionally content.
    """
    model = _base_model(api_path, os_path)
    if model is None:
        return None
    model["type"] = "file"
    model["mimetype"] = mimetypes.guess_type(os_path)[0]

    if content:
        try:
            with open(os_path, "rb") as f:
                raw = f.read()
        except OSError:
            return None

        if fmt == "base64":
            model["content"] = base64.b64encode(raw).decode("ascii")
            model["format"] = "base64"
        else:
            try:
                text = raw.decode("utf-8")
                model["content"] = text
                model["format"] = "text"
                if model["mimetype"] is None:
                    model["mimetype"] = "text/plain"
            except UnicodeDecodeError:
                model["content"] = base64.b64encode(raw).decode("ascii")
                model["format"] = "base64"
                if model["mimetype"] is None:
                    model["mimetype"] = "application/octet-stream"

    return model


# ---- Routes ----

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ping")
def ping():
    return jsonify({"status": "ok"}), 200


@app.route("/api/status")
def api_status():
    """Server status. No authentication required."""
    return jsonify({
        "started": datetime.now(timezone.utc).isoformat(),
        "version": "2.3.1",
        "pid": SERVER_PID,
    })


@app.route("/api/session", methods=["POST"])
def create_session():
    """Authenticate and create a session.

    POST /api/session
    JSON body: {"username": "...", "password": "..."}
    Returns: {"token": "...", "username": "...", "role": "..."}
    """
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"message": "JSON body required"}), 400

    username = body.get("username", "")
    password = body.get("password", "")

    user = _users.get(username)
    if not user or user["password"] != password:
        return jsonify({"message": "Invalid credentials"}), 401

    token = _create_session(username, user["role"])
    return jsonify({
        "token": token,
        "username": username,
        "role": user["role"],
    })


@app.route("/api/session", methods=["GET"])
@require_auth
def get_session():
    """Get current session info."""
    token = request.args.get("token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("token "):
            token = auth_header[6:]
    session = _active_sessions.get(token, {})
    return jsonify(session)


@app.route("/api/workspace", defaults={"path": ""}, methods=["GET"])
@app.route("/api/workspace/<path:path>", methods=["GET"])
@require_auth
def get_content(path=""):
    """Return a model for a file or directory.

    A directory model contains a list of models (without content)
    of the files and directories it contains.
    """
    api_path = path.strip("/")
    os_path = _get_os_path(api_path)

    if os_path is None:
        return jsonify({"message": "Invalid path"}), 400

    if not os.path.exists(os_path):
        return jsonify({"message": f"No such file or directory: {api_path}"}), 404

    content_flag = request.args.get("content", "1")
    include_content = content_flag == "1"
    req_type = request.args.get("type", None)
    req_format = request.args.get("format", None)

    if os.path.isdir(os_path):
        if req_type and req_type != "directory":
            return jsonify({"message": f"{api_path} is a directory, not a {req_type}"}), 400
        model = _dir_model(api_path, os_path, content=include_content)
        if model is None:
            return jsonify({"message": f"No such file or directory: {api_path}"}), 404
    else:
        if req_type == "directory":
            return jsonify({"message": f"{api_path} is not a directory"}), 400
        model = _file_model(api_path, os_path, content=include_content, fmt=req_format)
        if model is None:
            return jsonify({"message": f"No such file or directory: {api_path}"}), 404

    return jsonify(model)


@app.route("/api/workspace", defaults={"path": ""}, methods=["PUT"])
@app.route("/api/workspace/<path:path>", methods=["PUT"])
@require_auth
def save_content(path=""):
    """Save or create a file/directory."""
    api_path = path.strip("/")
    os_path = _get_os_path(api_path)

    if os_path is None:
        return jsonify({"message": "Invalid path"}), 400

    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"message": "JSON body required"}), 400

    file_type = body.get("type", "file")

    if file_type == "directory":
        if _is_hidden(os_path, WORKSPACE_ROOT) and not SHOW_HIDDEN:
            return jsonify({"message": "Cannot create hidden directory"}), 400
        os.makedirs(os_path, exist_ok=True)
        model = _dir_model(api_path, os_path, content=False)
        return jsonify(model), 201
    else:
        content = body.get("content", "")
        fmt = body.get("format", "text")

        parent_dir = os.path.dirname(os_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        try:
            if fmt == "base64":
                raw = base64.b64decode(content)
            else:
                raw = content.encode("utf-8")

            with open(os_path, "wb") as f:
                f.write(raw)
        except Exception:
            return jsonify({"message": "Error saving file"}), 500

        model = _file_model(api_path, os_path, content=False)
        if model is None:
            return jsonify({"message": "Error reading saved file"}), 500

        return jsonify(model), 201


@app.route("/api/workspace/<path:path>", methods=["DELETE"])
@require_auth
def delete_content(path):
    """Delete a file or directory."""
    api_path = path.strip("/")
    os_path = _get_os_path(api_path)

    if os_path is None:
        return jsonify({"message": "Invalid path"}), 400

    if not os.path.exists(os_path):
        return jsonify({"message": f"No such file or directory: {api_path}"}), 404

    try:
        if os.path.isdir(os_path):
            import shutil
            shutil.rmtree(os_path)
        else:
            os.unlink(os_path)
    except OSError:
        return jsonify({"message": "Error deleting resource"}), 500

    return "", 204


@app.route("/api/workspace/<path:path>", methods=["PATCH"])
@require_auth
def rename_content(path):
    """Rename (move) a file or directory."""
    api_path = path.strip("/")
    os_path = _get_os_path(api_path)

    if os_path is None:
        return jsonify({"message": "Invalid path"}), 400

    if not os.path.exists(os_path):
        return jsonify({"message": f"No such file or directory: {api_path}"}), 404

    body = request.get_json(silent=True)
    if body is None or "path" not in body:
        return jsonify({"message": "JSON body with 'path' field required"}), 400

    new_api_path = body["path"].strip("/")
    new_os_path = _get_os_path(new_api_path)

    if new_os_path is None:
        return jsonify({"message": "Invalid target path"}), 400

    if os.path.exists(new_os_path):
        return jsonify({"message": f"Already exists: {new_api_path}"}), 409

    import shutil
    try:
        new_parent = os.path.dirname(new_os_path)
        os.makedirs(new_parent, exist_ok=True)
        shutil.move(os_path, new_os_path)
    except Exception:
        return jsonify({"message": "Error renaming resource"}), 500

    if os.path.isdir(new_os_path):
        model = _dir_model(new_api_path, new_os_path, content=False)
    else:
        model = _file_model(new_api_path, new_os_path, content=False)

    return jsonify(model)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"message": "Internal server error"}), 500


with app.app_context():
    _initialize_server()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
