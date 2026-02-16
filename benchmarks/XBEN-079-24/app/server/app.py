import json
import logging
import os
import time
import uuid
import urllib.parse
import posixpath
from functools import wraps

from flask import Flask, Response, jsonify, request, send_file

app = Flask(__name__)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("trackml")

TRACKING_DIR = os.environ.get("TRACKML_TRACKING_DIR", "/data/tracking")
ARTIFACT_ROOT = os.environ.get("TRACKML_ARTIFACT_ROOT", "/data/artifacts")
VERSION = "1.8.2"

os.makedirs(TRACKING_DIR, exist_ok=True)
os.makedirs(ARTIFACT_ROOT, exist_ok=True)


# ============================================================
# In-memory store for experiments and runs
# ============================================================

class TrackingStore:
    def __init__(self, tracking_dir, artifact_root):
        self.tracking_dir = tracking_dir
        self.artifact_root = artifact_root
        self.experiments = {}
        self.runs = {}
        self._next_experiment_id = 1
        self._init_default_experiment()

    def _init_default_experiment(self):
        default_loc = os.path.join(self.artifact_root, "0")
        self.experiments["0"] = {
            "experiment_id": "0",
            "name": "Default",
            "artifact_location": default_loc,
            "lifecycle_stage": "active",
            "creation_time": int(time.time() * 1000),
            "last_update_time": int(time.time() * 1000),
            "tags": {}
        }
        os.makedirs(default_loc, exist_ok=True)

    def create_experiment(self, name, artifact_location=None, tags=None):
        for exp in self.experiments.values():
            if exp["name"] == name and exp["lifecycle_stage"] == "active":
                raise ValueError(f"Experiment with name '{name}' already exists")

        exp_id = str(self._next_experiment_id)
        self._next_experiment_id += 1

        if not artifact_location:
            resolved_location = os.path.join(self.artifact_root, exp_id)
        else:
            resolved_location = _resolve_local_uri(artifact_location)

        self.experiments[exp_id] = {
            "experiment_id": exp_id,
            "name": name,
            "artifact_location": resolved_location,
            "lifecycle_stage": "active",
            "creation_time": int(time.time() * 1000),
            "last_update_time": int(time.time() * 1000),
            "tags": tags or {}
        }

        # Create the artifact directory for experiments with local storage
        try:
            local_path = _uri_to_local_path(resolved_location)
            if local_path:
                os.makedirs(local_path, exist_ok=True)
        except Exception:
            pass

        return exp_id

    def get_experiment(self, experiment_id):
        exp = self.experiments.get(experiment_id)
        if exp is None or exp["lifecycle_stage"] == "deleted":
            return None
        return exp

    def search_experiments(self, view_type="ACTIVE_ONLY", max_results=1000):
        results = []
        for exp in self.experiments.values():
            if view_type == "ACTIVE_ONLY" and exp["lifecycle_stage"] != "active":
                continue
            if view_type == "DELETED_ONLY" and exp["lifecycle_stage"] != "deleted":
                continue
            results.append(exp)
        return results[:max_results]

    def delete_experiment(self, experiment_id):
        exp = self.experiments.get(experiment_id)
        if exp is None:
            raise ValueError(f"Experiment '{experiment_id}' not found")
        exp["lifecycle_stage"] = "deleted"
        exp["last_update_time"] = int(time.time() * 1000)

    def restore_experiment(self, experiment_id):
        exp = self.experiments.get(experiment_id)
        if exp is None:
            raise ValueError(f"Experiment '{experiment_id}' not found")
        exp["lifecycle_stage"] = "active"
        exp["last_update_time"] = int(time.time() * 1000)

    def update_experiment(self, experiment_id, new_name):
        exp = self.experiments.get(experiment_id)
        if exp is None:
            raise ValueError(f"Experiment '{experiment_id}' not found")
        exp["name"] = new_name
        exp["last_update_time"] = int(time.time() * 1000)

    def create_run(self, experiment_id, run_name=None, tags=None):
        exp = self.get_experiment(experiment_id)
        if exp is None:
            raise ValueError(f"Experiment '{experiment_id}' not found")

        run_id = uuid.uuid4().hex
        artifact_uri = _append_to_uri_path(
            exp["artifact_location"], run_id, "artifacts"
        )

        self.runs[run_id] = {
            "run_id": run_id,
            "run_name": run_name or "",
            "experiment_id": experiment_id,
            "status": "RUNNING",
            "start_time": int(time.time() * 1000),
            "end_time": 0,
            "artifact_uri": artifact_uri,
            "lifecycle_stage": "active",
            "metrics": {},
            "params": {},
            "tags": tags or {}
        }

        try:
            local_path = _uri_to_local_path(artifact_uri)
            if local_path:
                os.makedirs(local_path, exist_ok=True)
        except Exception:
            pass

        return self.runs[run_id]

    def get_run(self, run_id):
        run = self.runs.get(run_id)
        if run is None:
            raise ValueError(f"Run '{run_id}' not found")
        return run

    def update_run(self, run_id, status=None, end_time=None, run_name=None):
        run = self.get_run(run_id)
        if status:
            run["status"] = status
        if end_time:
            run["end_time"] = end_time
        if run_name:
            run["run_name"] = run_name
        return run

    def log_metric(self, run_id, key, value, timestamp=None, step=0):
        run = self.get_run(run_id)
        run["metrics"][key] = {
            "key": key,
            "value": value,
            "timestamp": timestamp or int(time.time() * 1000),
            "step": step
        }

    def log_param(self, run_id, key, value):
        run = self.get_run(run_id)
        run["params"][key] = {"key": key, "value": value}

    def set_tag(self, run_id, key, value):
        run = self.get_run(run_id)
        run["tags"][key] = value

    def search_runs(self, experiment_ids, max_results=1000):
        results = []
        for run in self.runs.values():
            if run["experiment_id"] in experiment_ids:
                results.append(run)
        return results[:max_results]


_store = TrackingStore(TRACKING_DIR, ARTIFACT_ROOT)


# ============================================================
# URI handling utilities
# ============================================================

def _resolve_local_uri(uri):
    """Resolve a local URI to an absolute form, preserving all URI components."""
    if uri is None:
        return None
    parsed = urllib.parse.urlparse(uri)
    scheme = parsed.scheme
    if scheme in ("", "file"):
        local_path = parsed.path
        if not os.path.isabs(local_path):
            local_path = os.path.join(os.getcwd(), local_path)
        if scheme == "file":
            return urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                local_path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
        return local_path
    return uri


def _uri_to_local_path(uri):
    """Convert a storage URI to a local filesystem path.

    For file:// URIs this strips the scheme and extracts the path
    component. For plain filesystem paths this is a no-op.
    """
    if uri.startswith("file://"):
        # Strip the file:// scheme to get the local path.
        # This handles file:///absolute/path -> /absolute/path
        path = uri[len("file://"):]
        return os.path.normpath(path)
    elif uri.startswith(("http:", "https:", "s3:", "gs:", "wasbs:")):
        return None
    return os.path.normpath(uri)


def _append_to_uri_path(uri, *paths):
    """Append path components to a URI while preserving scheme, host,
    query, and fragment information."""
    parsed = urllib.parse.urlparse(uri)

    # Validate query string for traversal sequences
    _check_query_string(parsed.query)

    combined = ""
    for p in paths:
        combined = posixpath.join(combined, p) if combined else p

    if len(parsed.scheme) == 0:
        return posixpath.join(uri, combined)

    new_path = posixpath.join(parsed.path, combined)
    new_parsed = parsed._replace(path=new_path)
    return urllib.parse.urlunparse(new_parsed)


def _check_query_string(query):
    """Validate query string does not contain traversal sequences."""
    decoded = _decode_uri(query)
    if ".." in decoded:
        raise ValueError("Invalid query string: traversal sequences not allowed")


def _validate_safe_path(path):
    """Validate that a path is safe to use (no traversal)."""
    decoded = _decode_uri(path)
    if "#" in decoded:
        raise ValueError("Invalid path")
    if ".." in decoded.split("/"):
        raise ValueError("Invalid path: traversal not allowed")
    if os.path.isabs(decoded):
        raise ValueError("Invalid path: absolute paths not allowed")
    return decoded


def _decode_uri(url):
    """Iteratively decode URL-encoded characters."""
    for _ in range(10):
        decoded = urllib.parse.unquote(url)
        if decoded == url:
            return url
        url = decoded
    raise ValueError("Failed to decode URL")


def _resolve_artifact_path(artifact_uri, relative_path=None):
    """Resolve the local filesystem path for an artifact."""
    local_path = _uri_to_local_path(artifact_uri)
    if local_path is None:
        return None
    if relative_path:
        return os.path.normpath(os.path.join(local_path, relative_path))
    return local_path


def _list_local_artifacts(base_dir, relative_path=None):
    """List artifacts in a local directory."""
    list_dir = os.path.join(base_dir, relative_path) if relative_path else base_dir
    if not os.path.isdir(list_dir):
        return []

    results = []
    for entry in sorted(os.listdir(list_dir)):
        full = os.path.join(list_dir, entry)
        rel = os.path.join(relative_path, entry) if relative_path else entry
        results.append({
            "path": rel,
            "is_dir": os.path.isdir(full),
            "file_size": os.path.getsize(full) if os.path.isfile(full) else 0
        })
    return results


# ============================================================
# Error handling
# ============================================================

class TrackMLError(Exception):
    def __init__(self, message, error_code="INTERNAL_ERROR"):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


def _error_response(message, error_code="INTERNAL_ERROR", status=500):
    return jsonify({"error_code": error_code, "message": message}), status


def catch_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except TrackMLError as e:
            return _error_response(e.message, e.error_code, 400)
        except ValueError as e:
            return _error_response(str(e), "INVALID_PARAMETER_VALUE", 400)
        except FileNotFoundError:
            return _error_response("Resource not found", "RESOURCE_DOES_NOT_EXIST", 404)
        except Exception:
            return _error_response("An internal error occurred", "INTERNAL_ERROR", 500)
    return wrapper


# ============================================================
# Health and info endpoints
# ============================================================

@app.route("/")
def index():
    return Response(
        json.dumps({"name": "TrackML Experiment Server", "version": VERSION}),
        mimetype="application/json"
    )


@app.route("/health")
def health():
    return "OK", 200


@app.route("/version")
def version():
    return VERSION, 200


# ============================================================
# Experiment APIs
# ============================================================

@app.route("/api/2.0/trackml/experiments/create", methods=["POST"])
@catch_errors
def create_experiment():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise TrackMLError("Invalid request body", "BAD_REQUEST")

    name = data.get("name")
    if not name:
        raise TrackMLError("Missing required parameter 'name'", "INVALID_PARAMETER_VALUE")

    artifact_location = data.get("artifact_location", "")
    tags_raw = data.get("tags", [])
    tags = {t["key"]: t["value"] for t in tags_raw if "key" in t and "value" in t}

    if artifact_location:
        parsed_loc = urllib.parse.urlparse(artifact_location)
        _check_query_string(parsed_loc.query)

    experiment_id = _store.create_experiment(name, artifact_location, tags)
    return jsonify({"experiment_id": experiment_id})


@app.route("/api/2.0/trackml/experiments/get", methods=["GET"])
@catch_errors
def get_experiment():
    experiment_id = request.args.get("experiment_id")
    if not experiment_id:
        raise TrackMLError("Missing required parameter 'experiment_id'", "INVALID_PARAMETER_VALUE")

    exp = _store.get_experiment(experiment_id)
    if exp is None:
        raise TrackMLError(f"Experiment '{experiment_id}' not found", "RESOURCE_DOES_NOT_EXIST")

    return jsonify({"experiment": exp})


@app.route("/api/2.0/trackml/experiments/search", methods=["POST", "GET"])
@catch_errors
def search_experiments():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
    else:
        data = request.args.to_dict()

    view_type = data.get("view_type", "ACTIVE_ONLY")
    max_results = int(data.get("max_results", 1000))
    experiments = _store.search_experiments(view_type, max_results)
    return jsonify({"experiments": experiments})


@app.route("/api/2.0/trackml/experiments/delete", methods=["POST"])
@catch_errors
def delete_experiment():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise TrackMLError("Invalid request body", "BAD_REQUEST")

    experiment_id = data.get("experiment_id")
    if not experiment_id:
        raise TrackMLError("Missing required parameter 'experiment_id'", "INVALID_PARAMETER_VALUE")

    _store.delete_experiment(experiment_id)
    return jsonify({})


@app.route("/api/2.0/trackml/experiments/restore", methods=["POST"])
@catch_errors
def restore_experiment():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise TrackMLError("Invalid request body", "BAD_REQUEST")

    experiment_id = data.get("experiment_id")
    if not experiment_id:
        raise TrackMLError("Missing required parameter 'experiment_id'", "INVALID_PARAMETER_VALUE")

    _store.restore_experiment(experiment_id)
    return jsonify({})


@app.route("/api/2.0/trackml/experiments/update", methods=["POST"])
@catch_errors
def update_experiment():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise TrackMLError("Invalid request body", "BAD_REQUEST")

    experiment_id = data.get("experiment_id")
    new_name = data.get("new_name")
    if not experiment_id:
        raise TrackMLError("Missing required parameter 'experiment_id'", "INVALID_PARAMETER_VALUE")
    if not new_name:
        raise TrackMLError("Missing required parameter 'new_name'", "INVALID_PARAMETER_VALUE")

    _store.update_experiment(experiment_id, new_name)
    return jsonify({})


# ============================================================
# Run APIs
# ============================================================

@app.route("/api/2.0/trackml/runs/create", methods=["POST"])
@catch_errors
def create_run():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise TrackMLError("Invalid request body", "BAD_REQUEST")

    experiment_id = data.get("experiment_id", "0")
    run_name = data.get("run_name", "")
    tags_raw = data.get("tags", [])
    tags = {t["key"]: t["value"] for t in tags_raw if "key" in t and "value" in t}

    run = _store.create_run(experiment_id, run_name, tags)

    return jsonify({
        "run": {
            "info": {
                "run_id": run["run_id"],
                "run_name": run["run_name"],
                "experiment_id": run["experiment_id"],
                "status": run["status"],
                "start_time": run["start_time"],
                "end_time": run["end_time"],
                "artifact_uri": run["artifact_uri"],
                "lifecycle_stage": run["lifecycle_stage"]
            },
            "data": {
                "metrics": list(run["metrics"].values()),
                "params": list(run["params"].values()),
                "tags": [{"key": k, "value": v} for k, v in run["tags"].items()]
            }
        }
    })


@app.route("/api/2.0/trackml/runs/get", methods=["GET"])
@catch_errors
def get_run():
    run_id = request.args.get("run_id")
    if not run_id:
        raise TrackMLError("Missing required parameter 'run_id'", "INVALID_PARAMETER_VALUE")

    run = _store.get_run(run_id)
    return jsonify({
        "run": {
            "info": {
                "run_id": run["run_id"],
                "run_name": run["run_name"],
                "experiment_id": run["experiment_id"],
                "status": run["status"],
                "start_time": run["start_time"],
                "end_time": run["end_time"],
                "artifact_uri": run["artifact_uri"],
                "lifecycle_stage": run["lifecycle_stage"]
            },
            "data": {
                "metrics": list(run["metrics"].values()),
                "params": list(run["params"].values()),
                "tags": [{"key": k, "value": v} for k, v in run["tags"].items()]
            }
        }
    })


@app.route("/api/2.0/trackml/runs/update", methods=["POST"])
@catch_errors
def update_run():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise TrackMLError("Invalid request body", "BAD_REQUEST")

    run_id = data.get("run_id")
    if not run_id:
        raise TrackMLError("Missing required parameter 'run_id'", "INVALID_PARAMETER_VALUE")

    status = data.get("status")
    end_time = data.get("end_time")
    run_name = data.get("run_name")

    run = _store.update_run(run_id, status, end_time, run_name)
    return jsonify({
        "run_info": {
            "run_id": run["run_id"],
            "status": run["status"],
            "end_time": run["end_time"]
        }
    })


@app.route("/api/2.0/trackml/runs/search", methods=["POST"])
@catch_errors
def search_runs():
    data = request.get_json(force=True, silent=True) or {}

    experiment_ids = data.get("experiment_ids", ["0"])
    max_results = int(data.get("max_results", 1000))

    runs = _store.search_runs(experiment_ids, max_results)
    return jsonify({
        "runs": [{
            "info": {
                "run_id": r["run_id"],
                "run_name": r["run_name"],
                "experiment_id": r["experiment_id"],
                "status": r["status"],
                "start_time": r["start_time"],
                "end_time": r["end_time"],
                "artifact_uri": r["artifact_uri"],
                "lifecycle_stage": r["lifecycle_stage"]
            },
            "data": {
                "metrics": list(r["metrics"].values()),
                "params": list(r["params"].values()),
                "tags": [{"key": k, "value": v} for k, v in r["tags"].items()]
            }
        } for r in runs]
    })


# ============================================================
# Metrics and Params
# ============================================================

@app.route("/api/2.0/trackml/runs/log-metric", methods=["POST"])
@catch_errors
def log_metric():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise TrackMLError("Invalid request body", "BAD_REQUEST")

    run_id = data.get("run_id")
    key = data.get("key")
    value = data.get("value")

    if not all([run_id, key, value is not None]):
        raise TrackMLError("Missing required parameters", "INVALID_PARAMETER_VALUE")

    _store.log_metric(run_id, key, float(value), data.get("timestamp"), data.get("step", 0))
    return jsonify({})


@app.route("/api/2.0/trackml/runs/log-parameter", methods=["POST"])
@catch_errors
def log_param():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise TrackMLError("Invalid request body", "BAD_REQUEST")

    run_id = data.get("run_id")
    key = data.get("key")
    value = data.get("value")

    if not all([run_id, key, value is not None]):
        raise TrackMLError("Missing required parameters", "INVALID_PARAMETER_VALUE")

    _store.log_param(run_id, key, str(value))
    return jsonify({})


@app.route("/api/2.0/trackml/runs/set-tag", methods=["POST"])
@catch_errors
def set_tag():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise TrackMLError("Invalid request body", "BAD_REQUEST")

    run_id = data.get("run_id")
    key = data.get("key")
    value = data.get("value")

    if not all([run_id, key, value is not None]):
        raise TrackMLError("Missing required parameters", "INVALID_PARAMETER_VALUE")

    _store.set_tag(run_id, key, str(value))
    return jsonify({})


# ============================================================
# Artifact APIs
# ============================================================

@app.route("/api/2.0/trackml/artifacts/list", methods=["GET"])
@catch_errors
def list_artifacts():
    run_id = request.args.get("run_id")
    if not run_id:
        raise TrackMLError("Missing required parameter 'run_id'", "INVALID_PARAMETER_VALUE")

    path = request.args.get("path")
    if path:
        path = _validate_safe_path(path)

    run = _store.get_run(run_id)
    artifact_uri = run["artifact_uri"]

    local_dir = _resolve_artifact_path(artifact_uri)
    if local_dir is None:
        return jsonify({"root_uri": artifact_uri, "files": []})

    files = _list_local_artifacts(local_dir, path)

    return jsonify({
        "root_uri": artifact_uri,
        "files": files
    })


@app.route("/api/2.0/trackml/artifacts/download", methods=["GET"])
@catch_errors
def download_artifact():
    run_id = request.args.get("run_id")
    path = request.args.get("path")

    if not run_id or not path:
        raise TrackMLError(
            "Missing required parameters 'run_id' and 'path'",
            "INVALID_PARAMETER_VALUE"
        )

    path = _validate_safe_path(path)

    run = _store.get_run(run_id)
    artifact_uri = run["artifact_uri"]

    local_path = _resolve_artifact_path(artifact_uri, path)
    if local_path is None or not os.path.isfile(local_path):
        raise TrackMLError("Artifact not found", "RESOURCE_DOES_NOT_EXIST")

    return send_file(local_path, as_attachment=True)


# ============================================================
# Batch logging
# ============================================================

@app.route("/api/2.0/trackml/runs/log-batch", methods=["POST"])
@catch_errors
def log_batch():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise TrackMLError("Invalid request body", "BAD_REQUEST")

    run_id = data.get("run_id")
    if not run_id:
        raise TrackMLError("Missing required parameter 'run_id'", "INVALID_PARAMETER_VALUE")

    for metric in data.get("metrics", []):
        _store.log_metric(run_id, metric["key"], float(metric["value"]),
                         metric.get("timestamp"), metric.get("step", 0))

    for param in data.get("params", []):
        _store.log_param(run_id, param["key"], str(param["value"]))

    for tag in data.get("tags", []):
        _store.set_tag(run_id, tag["key"], str(tag["value"]))

    return jsonify({})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
