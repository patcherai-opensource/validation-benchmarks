import os
import json
import uuid
import time
import logging
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.urandom(24).hex()

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('arrp')

# Base directories
BASE_DIR = Path('/opt/arrp')
DATA_DIR = BASE_DIR / 'data'
RESOURCES_DIR = DATA_DIR / 'resources'
OUTPUT_DIR = DATA_DIR / 'output'
PACKS_DIR = DATA_DIR / 'packs'

# In-memory resource pack store
resource_packs = {}


class RuntimeResourcePack:
    """Runtime resource pack implementation for managing mod resources."""

    def __init__(self, pack_id, name, description=""):
        self.pack_id = pack_id
        self.name = name
        self.description = description
        self.resources = {}
        self.created_at = time.time()
        self.pack_dir = PACKS_DIR / pack_id
        self.pack_dir.mkdir(parents=True, exist_ok=True)

    def add_resource(self, namespace, path_segments, data):
        """Add a resource entry. path_segments is a list of path components."""
        key = tuple([namespace] + path_segments)
        self.resources[key] = data
        return key

    def remove_resource(self, namespace, path_segments):
        """Remove a resource entry."""
        key = tuple([namespace] + path_segments)
        if key in self.resources:
            del self.resources[key]
            return True
        return False

    def dump_direct(self, output):
        """
        Dump all resources to the specified output directory.
        Writes each resource to disk based on its key path.
        """
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        results = []

        for key, data in self.resources.items():
            path_str = "/".join(key)
            path = output.resolve() / path_str

            # Validate the resolved path stays within output directory
            if str(path).startswith(str(output)):
                path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(data, str):
                    path.write_text(data)
                else:
                    path.write_bytes(data)
                results.append({"path": str(path), "status": "written"})
            else:
                results.append({"path": path_str, "status": "rejected", "reason": "path outside output directory"})

        return results

    def read_resource(self, output, namespace, path_segments):
        """
        Read a previously dumped resource from the output directory.
        """
        output = Path(output)
        path_str = "/".join([namespace] + path_segments)
        path = output.resolve() / path_str

        # Validate the resolved path stays within output directory
        if str(path).startswith(str(output)):
            if path.exists():
                return path.read_bytes()
            return None
        return None

    def to_dict(self):
        return {
            "pack_id": self.pack_id,
            "name": self.name,
            "description": self.description,
            "resource_count": len(self.resources),
            "created_at": self.created_at,
        }


def get_pack(pack_id):
    return resource_packs.get(pack_id)


# Health endpoint
@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200


# Main UI
@app.route('/')
def index():
    return render_template('index.html')


# API: List all packs
@app.route('/api/v1/packs', methods=['GET'])
def list_packs():
    packs = [p.to_dict() for p in resource_packs.values()]
    return jsonify({"packs": packs})


# API: Create a new resource pack
@app.route('/api/v1/packs', methods=['POST'])
def create_pack():
    data = request.get_json(silent=True)
    if not data or 'name' not in data:
        return jsonify({"error": "Missing required field: name"}), 400

    pack_id = str(uuid.uuid4())[:8]
    name = data['name']
    description = data.get('description', '')

    pack = RuntimeResourcePack(pack_id, name, description)
    resource_packs[pack_id] = pack

    return jsonify(pack.to_dict()), 201


# API: Get pack details
@app.route('/api/v1/packs/<pack_id>', methods=['GET'])
def get_pack_details(pack_id):
    pack = get_pack(pack_id)
    if not pack:
        return jsonify({"error": "Pack not found"}), 404

    resources = []
    for key in pack.resources:
        resources.append({"namespace": key[0], "path": "/".join(key[1:])})

    result = pack.to_dict()
    result["resources"] = resources
    return jsonify(result)


# API: Delete a pack
@app.route('/api/v1/packs/<pack_id>', methods=['DELETE'])
def delete_pack(pack_id):
    if pack_id in resource_packs:
        del resource_packs[pack_id]
        return jsonify({"status": "deleted"}), 200
    return jsonify({"error": "Pack not found"}), 404


# API: Add a resource to a pack
@app.route('/api/v1/packs/<pack_id>/resources', methods=['POST'])
def add_resource(pack_id):
    pack = get_pack(pack_id)
    if not pack:
        return jsonify({"error": "Pack not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    namespace = data.get('namespace', 'minecraft')
    path_segments = data.get('path', [])
    content = data.get('content', '')

    if not isinstance(path_segments, list) or len(path_segments) == 0:
        return jsonify({"error": "path must be a non-empty array of path segments"}), 400

    key = pack.add_resource(namespace, path_segments, content.encode('utf-8') if isinstance(content, str) else content)

    return jsonify({
        "status": "added",
        "namespace": namespace,
        "path": "/".join(path_segments),
        "key": "/".join(key)
    }), 201


# API: Remove a resource from a pack
@app.route('/api/v1/packs/<pack_id>/resources', methods=['DELETE'])
def remove_resource(pack_id):
    pack = get_pack(pack_id)
    if not pack:
        return jsonify({"error": "Pack not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    namespace = data.get('namespace', 'minecraft')
    path_segments = data.get('path', [])

    if pack.remove_resource(namespace, path_segments):
        return jsonify({"status": "removed"}), 200
    return jsonify({"error": "Resource not found"}), 404


# API: Dump pack resources to output directory
@app.route('/api/v1/packs/<pack_id>/dump', methods=['POST'])
def dump_pack(pack_id):
    pack = get_pack(pack_id)
    if not pack:
        return jsonify({"error": "Pack not found"}), 404

    output_dir = OUTPUT_DIR / pack_id
    results = pack.dump_direct(output_dir)

    return jsonify({
        "status": "dumped",
        "output_directory": str(output_dir),
        "results": results
    })


# API: Read a dumped resource
@app.route('/api/v1/packs/<pack_id>/read', methods=['POST'])
def read_resource(pack_id):
    pack = get_pack(pack_id)
    if not pack:
        return jsonify({"error": "Pack not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    namespace = data.get('namespace', 'minecraft')
    path_segments = data.get('path', [])

    if not isinstance(path_segments, list) or len(path_segments) == 0:
        return jsonify({"error": "path must be a non-empty array of path segments"}), 400

    output_dir = OUTPUT_DIR / pack_id
    content = pack.read_resource(output_dir, namespace, path_segments)

    if content is not None:
        try:
            return jsonify({"content": content.decode('utf-8'), "encoding": "utf-8"})
        except UnicodeDecodeError:
            import base64
            return jsonify({"content": base64.b64encode(content).decode(), "encoding": "base64"})
    return jsonify({"error": "Resource not found or path invalid"}), 404


# API: Documentation
@app.route('/api/v1/docs')
def api_docs():
    return jsonify({
        "name": "ARRP Resource Pack Manager",
        "version": "0.8.1",
        "endpoints": [
            {"method": "GET", "path": "/api/v1/packs", "description": "List all resource packs"},
            {"method": "POST", "path": "/api/v1/packs", "description": "Create a new resource pack", "body": {"name": "string", "description": "string (optional)"}},
            {"method": "GET", "path": "/api/v1/packs/<pack_id>", "description": "Get pack details and resource listing"},
            {"method": "DELETE", "path": "/api/v1/packs/<pack_id>", "description": "Delete a resource pack"},
            {"method": "POST", "path": "/api/v1/packs/<pack_id>/resources", "description": "Add a resource to a pack", "body": {"namespace": "string", "path": ["array", "of", "segments"], "content": "string"}},
            {"method": "DELETE", "path": "/api/v1/packs/<pack_id>/resources", "description": "Remove a resource from a pack"},
            {"method": "POST", "path": "/api/v1/packs/<pack_id>/dump", "description": "Dump pack resources to output directory"},
            {"method": "POST", "path": "/api/v1/packs/<pack_id>/read", "description": "Read a previously dumped resource"},
        ]
    })


# Static assets
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


# Suppress default error details
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == '__main__':
    # Ensure directories exist
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PACKS_DIR.mkdir(parents=True, exist_ok=True)

    app.run(host='0.0.0.0', port=80, debug=False)
