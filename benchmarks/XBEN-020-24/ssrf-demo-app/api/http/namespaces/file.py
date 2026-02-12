"""
File management API namespace.

Handles file uploads and URL-based file imports for use as data sources.
"""

import os
import uuid
import json
import logging
from datetime import datetime

import requests
from flask import Blueprint, request, jsonify

from security import is_private_url
from config import Config

logger = logging.getLogger(__name__)

file_bp = Blueprint('files', __name__)

# In-memory file registry (simulates database)
_file_registry = {}


def _save_file_metadata(name, metadata):
    """Save file metadata to registry."""
    _file_registry[name] = metadata
    # Also persist to disk
    meta_path = os.path.join(Config.FILES_DIR, '.registry.json')
    try:
        existing = {}
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                existing = json.load(f)
        existing[name] = metadata
        with open(meta_path, 'w') as f:
            json.dump(existing, f)
    except Exception:
        pass


def _get_file_metadata(name):
    """Get file metadata from registry."""
    if name in _file_registry:
        return _file_registry[name]
    meta_path = os.path.join(Config.FILES_DIR, '.registry.json')
    try:
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                data = json.load(f)
            return data.get(name)
    except Exception:
        pass
    return None


@file_bp.route('/files', methods=['GET'])
def list_files():
    """List all uploaded files."""
    meta_path = os.path.join(Config.FILES_DIR, '.registry.json')
    files = {}
    try:
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                files = json.load(f)
    except Exception:
        pass

    result = []
    for name, meta in files.items():
        result.append({
            'name': name,
            'source_type': meta.get('source_type', 'unknown'),
            'created_at': meta.get('created_at', ''),
            'size': meta.get('size', 0),
        })
    return jsonify(result), 200


@file_bp.route('/files/<name>', methods=['PUT'])
def upload_file(name):
    """Upload or import a file.

    Supports two source types:
    - 'file': Direct file upload via multipart form data
    - 'url': Import file from a remote URL

    For URL imports, SSRF protection is applied to prevent access to
    internal/private network resources.
    """
    source_type = request.args.get('source_type', request.form.get('source_type', ''))

    if not source_type:
        return jsonify({'error': 'source_type parameter is required (file or url)'}), 400

    if source_type == 'file':
        return _handle_file_upload(name)
    elif source_type == 'url':
        return _handle_url_import(name)
    else:
        return jsonify({'error': 'Invalid source_type. Must be "file" or "url"'}), 400


def _handle_file_upload(name):
    """Handle direct file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided in request'}), 400

    uploaded = request.files['file']
    if uploaded.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    file_path = os.path.join(Config.FILES_DIR, f'{name}_{uuid.uuid4().hex[:8]}')
    uploaded.save(file_path)

    metadata = {
        'name': name,
        'source_type': 'file',
        'original_filename': uploaded.filename,
        'path': file_path,
        'size': os.path.getsize(file_path),
        'created_at': datetime.utcnow().isoformat(),
    }
    _save_file_metadata(name, metadata)

    return jsonify({'message': f'File "{name}" uploaded successfully', 'name': name}), 200


def _handle_url_import(name):
    """Handle URL-based file import with SSRF protection."""
    source = request.args.get('source', request.form.get('source', ''))

    if not source:
        return jsonify({'error': 'source parameter is required for URL imports'}), 400

    # Validate URL format
    if not source.startswith(('http://', 'https://')):
        return jsonify({'error': 'URL must start with http:// or https://'}), 400

    # SSRF protection: check if URL resolves to a private address
    if Config.CLOUD and is_private_url(source):
        return jsonify({'error': 'Access to private/internal URLs is restricted'}), 403

    # Fetch the remote resource
    try:
        response = requests.get(source, stream=True, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request to URL timed out'}), 408
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Failed to connect to the specified URL'}), 502
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'HTTP error from remote server: {e.response.status_code}'}), 502
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Failed to fetch URL'}), 500

    # Save fetched content to file
    file_path = os.path.join(Config.FILES_DIR, f'{name}_{uuid.uuid4().hex[:8]}')
    content_size = 0
    try:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    content_size += len(chunk)
    except Exception:
        return jsonify({'error': 'Failed to save fetched content'}), 500

    metadata = {
        'name': name,
        'source_type': 'url',
        'source_url': source,
        'path': file_path,
        'size': content_size,
        'created_at': datetime.utcnow().isoformat(),
    }
    _save_file_metadata(name, metadata)

    return jsonify({
        'message': f'File "{name}" imported successfully from URL',
        'name': name,
        'size': content_size,
    }), 200


@file_bp.route('/files/<name>', methods=['GET'])
def get_file(name):
    """Get file metadata and content preview."""
    metadata = _get_file_metadata(name)
    if metadata is None:
        return jsonify({'error': f'File "{name}" not found'}), 404

    result = {
        'name': metadata.get('name'),
        'source_type': metadata.get('source_type'),
        'size': metadata.get('size', 0),
        'created_at': metadata.get('created_at', ''),
    }

    # Include content preview for small files
    file_path = metadata.get('path', '')
    if os.path.exists(file_path) and metadata.get('size', 0) < 1024 * 1024:
        try:
            with open(file_path, 'r', errors='replace') as f:
                result['content_preview'] = f.read(4096)
        except Exception:
            result['content_preview'] = None

    return jsonify(result), 200


@file_bp.route('/files/<name>', methods=['DELETE'])
def delete_file(name):
    """Delete a file."""
    metadata = _get_file_metadata(name)
    if metadata is None:
        return jsonify({'error': f'File "{name}" not found'}), 404

    # Remove the actual file
    file_path = metadata.get('path', '')
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    # Remove from registry
    if name in _file_registry:
        del _file_registry[name]

    meta_path = os.path.join(Config.FILES_DIR, '.registry.json')
    try:
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                data = json.load(f)
            if name in data:
                del data[name]
            with open(meta_path, 'w') as f:
                json.dump(data, f)
    except Exception:
        pass

    return jsonify({'message': f'File "{name}" deleted'}), 200
