import os
import json
import base64
import hashlib
import hmac
import uuid
import time
import csv
import io
import tarfile
from datetime import datetime

from flask import (
    Flask, render_template, request, jsonify, redirect,
    url_for, send_file, abort, Response, make_response
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

SERVICE_NAME = "DataRefinery"
VERSION = "3.7.2"

# In-memory project store
projects = {}
project_counter = 0

# Extension registry
EXTENSIONS = {
    "cloudstore-connector": {
        "name": "Cloud Storage Connector",
        "version": "1.4.0",
        "description": "Import and export data from cloud storage services (S3, GCS, Azure Blob)",
        "author": "DataRefinery Contributors",
        "requires": "core",
        "status": "stable"
    },
    "database-connector": {
        "name": "Database Connector",
        "version": "2.1.3",
        "description": "Connect to MySQL, PostgreSQL, SQLite and other databases",
        "author": "DataRefinery Contributors",
        "requires": "core",
        "status": "stable"
    },
    "wikidata-integration": {
        "name": "Wikidata Integration",
        "version": "0.9.1",
        "description": "Reconcile and upload data to Wikidata",
        "author": "DataRefinery Contributors",
        "requires": "core",
        "status": "beta"
    }
}

# Storage API credentials - used by the cloudstore connector extension
# These are configured via system properties or defaults are used
_STORAGE_API_KEY = os.environ.get(
    "ext.cloudstore.apikey",
    base64.b64decode(b'ZHJmLWludGVybmFsLWFwaS1rZXktNzM5MjFhYmNkZWY=').decode('utf-8')
)
_STORAGE_API_SECRET = os.environ.get(
    "ext.cloudstore.apisecret",
    base64.b64decode(b'aDdSMmtXOXBMbU56WVhOelpYUTlOM1J5TkhrMk5EWnpNMk55WlRR').decode('utf-8')
)


def _verify_api_credentials(api_key, api_secret):
    return (
        hmac.compare_digest(api_key, _STORAGE_API_KEY)
        and hmac.compare_digest(api_secret, _STORAGE_API_SECRET)
    )


# ─── Main UI Routes ──────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html', version=VERSION, projects=projects)


@app.route('/ping')
def ping():
    return jsonify({"status": "ok", "service": SERVICE_NAME, "version": VERSION})


# ─── Project Management ──────────────────────────────────────────

@app.route('/command/core/create-project', methods=['POST'])
def create_project():
    global project_counter
    name = request.form.get('project-name', 'Untitled')
    project_counter += 1
    pid = project_counter
    projects[pid] = {
        "id": pid,
        "name": name,
        "created": datetime.utcnow().isoformat() + "Z",
        "modified": datetime.utcnow().isoformat() + "Z",
        "row_count": 0,
        "columns": [],
        "rows": []
    }
    return jsonify({"code": "ok", "projectID": pid})


@app.route('/command/core/get-all-project-metadata')
def get_all_project_metadata():
    metadata = {}
    for pid, proj in projects.items():
        metadata[str(pid)] = {
            "name": proj["name"],
            "created": proj["created"],
            "modified": proj["modified"],
            "rowCount": proj["row_count"]
        }
    return jsonify({"projects": metadata})


@app.route('/command/core/get-project-metadata')
def get_project_metadata():
    pid = request.args.get('project', type=int)
    if pid not in projects:
        return jsonify({"code": "error", "message": "Project not found"}), 404
    proj = projects[pid]
    return jsonify({
        "name": proj["name"],
        "created": proj["created"],
        "modified": proj["modified"],
        "rowCount": proj["row_count"],
        "columnModel": {"columns": [{"name": c} for c in proj["columns"]]}
    })


@app.route('/command/core/get-rows')
def get_rows():
    pid = request.args.get('project', type=int)
    start = request.args.get('start', 0, type=int)
    limit = request.args.get('limit', 25, type=int)
    if pid not in projects:
        return jsonify({"code": "error", "message": "Project not found"}), 404
    proj = projects[pid]
    rows = proj["rows"][start:start + limit]
    return jsonify({
        "mode": "row-based",
        "rows": rows,
        "total": proj["row_count"],
        "start": start,
        "limit": limit
    })


@app.route('/command/core/import-csv', methods=['POST'])
def import_csv():
    global project_counter
    if 'file' not in request.files:
        return jsonify({"code": "error", "message": "No file provided"}), 400
    f = request.files['file']
    name = request.form.get('project-name', f.filename or 'Untitled')
    try:
        content = f.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        columns = reader.fieldnames or []
        rows = []
        for i, row in enumerate(reader):
            cells = [{"v": row.get(c, "")} for c in columns]
            rows.append({"i": i, "cells": cells})
        project_counter += 1
        pid = project_counter
        projects[pid] = {
            "id": pid,
            "name": name,
            "created": datetime.utcnow().isoformat() + "Z",
            "modified": datetime.utcnow().isoformat() + "Z",
            "row_count": len(rows),
            "columns": columns,
            "rows": rows
        }
        return jsonify({"code": "ok", "projectID": pid, "rowCount": len(rows)})
    except Exception:
        return jsonify({"code": "error", "message": "Failed to parse CSV data"}), 400


@app.route('/command/core/delete-project', methods=['POST'])
def delete_project():
    pid = request.form.get('project', type=int)
    if pid and pid in projects:
        del projects[pid]
        return jsonify({"code": "ok"})
    return jsonify({"code": "error", "message": "Project not found"}), 404


# ─── Extensions ───────────────────────────────────────────────────

@app.route('/extensions')
def extensions_page():
    ext_list = []
    for eid, ext in EXTENSIONS.items():
        ext_list.append({
            "id": eid,
            "name": ext["name"],
            "version": ext["version"],
            "description": ext["description"],
            "status": ext["status"]
        })
    return render_template('extensions.html', version=VERSION, extensions=ext_list)


@app.route('/command/core/get-extensions')
def get_extensions():
    ext_list = []
    for eid, ext in EXTENSIONS.items():
        ext_list.append({
            "id": eid,
            "name": ext["name"],
            "version": ext["version"],
            "description": ext["description"],
            "status": ext["status"]
        })
    return jsonify({"extensions": ext_list})


@app.route('/extensions/<ext_id>/module/download')
def download_extension(ext_id):
    if ext_id not in EXTENSIONS:
        abort(404)
    ext = EXTENSIONS[ext_id]
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as tar:
        # module.properties
        props = f"name = {ext_id}\ndescription = {ext['description']}\nversion = {ext['version']}\nrequires = {ext['requires']}\n"
        props_info = tarfile.TarInfo(name=f"{ext_id}/module/MOD-INF/module.properties")
        props_data = props.encode('utf-8')
        props_info.size = len(props_data)
        tar.addfile(props_info, io.BytesIO(props_data))

        if ext_id == "cloudstore-connector":
            config_content = _generate_cloudstore_config()
            config_info = tarfile.TarInfo(name=f"{ext_id}/src/config/CloudStorageConfig.py")
            config_data = config_content.encode('utf-8')
            config_info.size = len(config_data)
            tar.addfile(config_info, io.BytesIO(config_data))

            init_content = _generate_cloudstore_init()
            init_info = tarfile.TarInfo(name=f"{ext_id}/src/connector/__init__.py")
            init_data = init_content.encode('utf-8')
            init_info.size = len(init_data)
            tar.addfile(init_info, io.BytesIO(init_data))

        elif ext_id == "database-connector":
            db_config = (
                "import os\n\nDB_DRIVERS = {\n"
                "    'mysql': 'mysqlclient',\n"
                "    'postgresql': 'psycopg2',\n"
                "    'sqlite': 'sqlite3'\n}\n\n"
                "DEFAULT_TIMEOUT = 30\n"
                "MAX_QUERY_ROWS = 10000\n"
            )
            db_info = tarfile.TarInfo(name=f"{ext_id}/src/config/DatabaseConfig.py")
            db_data = db_config.encode('utf-8')
            db_info.size = len(db_data)
            tar.addfile(db_info, io.BytesIO(db_data))

        elif ext_id == "wikidata-integration":
            wiki_config = (
                "WIKIDATA_API = 'https://www.wikidata.org/w/api.php'\n"
                "RECONCILIATION_ENDPOINT = 'https://wikidata.reconci.link/en/api'\n"
                "MAX_BATCH_SIZE = 50\n"
            )
            wiki_info = tarfile.TarInfo(name=f"{ext_id}/src/config/WikidataConfig.py")
            wiki_data = wiki_config.encode('utf-8')
            wiki_info.size = len(wiki_data)
            tar.addfile(wiki_info, io.BytesIO(wiki_data))

        readme = f"# {ext['name']}\n\n{ext['description']}\n\nVersion: {ext['version']}\n"
        readme_info = tarfile.TarInfo(name=f"{ext_id}/README.md")
        readme_data = readme.encode('utf-8')
        readme_info.size = len(readme_data)
        tar.addfile(readme_info, io.BytesIO(readme_data))

    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/gzip',
        as_attachment=True,
        download_name=f"{ext_id}-{ext['version']}.tar.gz"
    )


def _generate_cloudstore_config():
    return '''import os
import base64

SERVICE_APP_NAME = "DataRefinery-CloudStorage-Service"

# For a production release, these can be set via system properties
# or environment variables. The defaults are used for development builds.
STORAGE_API_KEY = os.environ.get(
    "ext.cloudstore.apikey",
    base64.b64decode(b'ZHJmLWludGVybmFsLWFwaS1rZXktNzM5MjFhYmNkZWY=').decode('utf-8')
)
STORAGE_API_SECRET = os.environ.get(
    "ext.cloudstore.apisecret",
    base64.b64decode(b'aDdSMmtXOXBMbU56WVhOelpYUTlOM1J5TkhrMk5EWnpNMk55WlRR').decode('utf-8')
)

STORAGE_ENDPOINT = "/api/v1/storage/objects"

CONNECT_TIMEOUT = 180000
READ_TIMEOUT = 180000

SUPPORTED_PROVIDERS = ["s3", "gcs", "azure-blob"]
MAX_UPLOAD_SIZE = 104857600  # 100MB
'''


def _generate_cloudstore_init():
    return '''from .config import CloudStorageConfig

class CloudStorageConnector:
    """Connector for cloud storage services."""

    def __init__(self):
        self.api_key = CloudStorageConfig.STORAGE_API_KEY
        self.api_secret = CloudStorageConfig.STORAGE_API_SECRET
        self.endpoint = CloudStorageConfig.STORAGE_ENDPOINT

    def list_objects(self, provider, bucket, prefix=""):
        """List objects in a cloud storage bucket."""
        pass

    def get_object(self, provider, bucket, key):
        """Retrieve an object from cloud storage."""
        pass

    def put_object(self, provider, bucket, key, data):
        """Upload an object to cloud storage."""
        pass
'''


# ─── Cloud Storage API (internal) ────────────────────────────────

@app.route('/api/v1/storage/objects', methods=['GET'])
def storage_list_objects():
    api_key = request.headers.get('X-Api-Key', '')
    api_secret = request.headers.get('X-Api-Secret', '')

    if not api_key or not api_secret:
        return jsonify({"error": "Authentication required"}), 401

    if not _verify_api_credentials(api_key, api_secret):
        return jsonify({"error": "Invalid credentials"}), 403

    bucket = request.args.get('bucket', 'default')
    prefix = request.args.get('prefix', '')

    objects = _get_storage_objects(bucket, prefix)
    return jsonify({"bucket": bucket, "prefix": prefix, "objects": objects})


@app.route('/api/v1/storage/objects/<path:object_key>', methods=['GET'])
def storage_get_object(object_key):
    api_key = request.headers.get('X-Api-Key', '')
    api_secret = request.headers.get('X-Api-Secret', '')

    if not api_key or not api_secret:
        return jsonify({"error": "Authentication required"}), 401

    if not _verify_api_credentials(api_key, api_secret):
        return jsonify({"error": "Invalid credentials"}), 403

    bucket = request.args.get('bucket', 'default')
    content = _get_object_content(bucket, object_key)
    if content is None:
        return jsonify({"error": "Object not found"}), 404

    return jsonify({"bucket": bucket, "key": object_key, "content": content})


def _get_storage_objects(bucket, prefix):
    objects = []
    storage_dir = f'/opt/datarefinery/data/storage'
    bucket_dir = os.path.join(storage_dir, bucket)
    if os.path.isdir(bucket_dir):
        for root, dirs, files in os.walk(bucket_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                relpath = os.path.relpath(fpath, bucket_dir)
                if prefix and not relpath.startswith(prefix):
                    continue
                stat = os.stat(fpath)
                objects.append({
                    "key": relpath,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z"
                })
    return objects


def _get_object_content(bucket, key):
    storage_dir = f'/opt/datarefinery/data/storage'
    fpath = os.path.join(storage_dir, bucket, key)
    fpath = os.path.realpath(fpath)
    if not fpath.startswith(os.path.realpath(storage_dir)):
        return None
    if os.path.isfile(fpath):
        with open(fpath, 'r') as f:
            return f.read()
    return None


# ─── Expression / Transform endpoints ────────────────────────────

@app.route('/command/core/preview-expression', methods=['POST'])
def preview_expression():
    pid = request.form.get('project', type=int)
    expression = request.form.get('expression', '')
    if pid not in projects:
        return jsonify({"code": "error", "message": "Project not found"}), 404
    return jsonify({
        "code": "ok",
        "results": [],
        "message": "Expression preview not available in this build"
    })


@app.route('/command/core/get-version')
def get_version():
    return jsonify({
        "version": VERSION,
        "revision": "a1b2c3d",
        "full_name": f"{SERVICE_NAME} {VERSION}",
        "java_runtime": "N/A"
    })


# ─── Error handlers ──────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/') or request.path.startswith('/command/'):
        return jsonify({"error": "Not found"}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

