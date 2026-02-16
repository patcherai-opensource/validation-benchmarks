from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response
import os
import json
import uuid
import time
import base64
import hashlib

from app import app, UPLOAD_DIR, INDEX_STORE
from app.models import VectorIndex, DocumentRecord


# In-memory registry of loaded indexes
_index_registry = {}


def _get_stored_indexes():
    """List index metadata files from disk."""
    indexes = []
    if os.path.isdir(INDEX_STORE):
        for fname in os.listdir(INDEX_STORE):
            if fname.endswith('.meta.json'):
                try:
                    with open(os.path.join(INDEX_STORE, fname), 'r') as f:
                        indexes.append(json.load(f))
                except Exception:
                    pass
    return indexes


def _save_index_meta(index_obj):
    """Persist index metadata to disk."""
    meta = index_obj.info()
    meta_path = os.path.join(INDEX_STORE, f"{meta['index_id']}.meta.json")
    with open(meta_path, 'w') as f:
        json.dump(meta, f)


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message="The requested resource was not found."), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message="An internal server error occurred."), 500


@app.route('/')
def dashboard():
    stored = _get_stored_indexes()
    loaded = {k: v.info() for k, v in _index_registry.items()}
    return render_template('dashboard.html', stored_indexes=stored, loaded_indexes=loaded)


@app.route('/indexes')
def list_indexes():
    stored = _get_stored_indexes()
    return render_template('indexes.html', indexes=stored)


@app.route('/api/v1/indexes', methods=['GET'])
def api_list_indexes():
    stored = _get_stored_indexes()
    return jsonify({"indexes": stored, "count": len(stored)})


@app.route('/indexes/create', methods=['GET', 'POST'])
def create_index():
    if request.method == 'GET':
        return render_template('create_index.html')

    name = request.form.get('name', '').strip()
    dimension = request.form.get('dimension', '128')
    metric = request.form.get('distance_metric', 'cosine')

    if not name:
        return render_template('create_index.html', error="Index name is required.")

    try:
        dimension = int(dimension)
        if dimension < 1 or dimension > 4096:
            raise ValueError()
    except (ValueError, TypeError):
        return render_template('create_index.html', error="Dimension must be an integer between 1 and 4096.")

    if metric not in ('cosine', 'euclidean', 'inner_product'):
        return render_template('create_index.html', error="Invalid distance metric.")

    idx = VectorIndex(name=name, dimension=dimension, distance_metric=metric)
    _index_registry[idx.index_id] = idx
    _save_index_meta(idx)

    return redirect(url_for('view_index', index_id=idx.index_id))


@app.route('/indexes/<index_id>')
def view_index(index_id):
    idx = _index_registry.get(index_id)
    if not idx:
        stored = _get_stored_indexes()
        meta = next((s for s in stored if s.get('index_id') == index_id), None)
        if meta:
            return render_template('view_index.html', index_info=meta, loaded=False)
        return render_template('error.html', code=404, message="Index not found."), 404

    info = idx.info()
    docs = [d.to_dict() for d in idx.docstore.list_all()]
    return render_template('view_index.html', index_info=info, loaded=True, documents=docs)


@app.route('/indexes/<index_id>/export', methods=['GET'])
def export_index(index_id):
    idx = _index_registry.get(index_id)
    if not idx:
        return render_template('error.html', code=404, message="Index not loaded in memory."), 404

    serialized = idx.serialize_to_bytes()
    encoded = base64.b64encode(serialized).decode('ascii')

    response = make_response(encoded)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = f'attachment; filename="{idx.name}_{idx.index_id}.vidx"'
    return response


@app.route('/indexes/import', methods=['GET', 'POST'])
def import_index():
    if request.method == 'GET':
        return render_template('import_index.html')

    uploaded_file = request.files.get('index_file')
    raw_data = request.form.get('serialized_data', '').strip()

    if not uploaded_file and not raw_data:
        return render_template('import_index.html',
                               error="Please provide an index file or paste serialized data.")

    try:
        if uploaded_file and uploaded_file.filename:
            content = uploaded_file.read()
            if not content:
                return render_template('import_index.html', error="Uploaded file is empty.")
            serialized = base64.b64decode(content)
        else:
            serialized = base64.b64decode(raw_data)

        idx = VectorIndex.restore_from_bytes(serialized)

        _index_registry[idx.index_id] = idx
        _save_index_meta(idx)

        return redirect(url_for('view_index', index_id=idx.index_id))

    except Exception as e:
        return render_template('import_index.html',
                               error="Failed to restore index. The data may be corrupted or in an unsupported format.")


@app.route('/indexes/<index_id>/documents', methods=['POST'])
def add_documents(index_id):
    idx = _index_registry.get(index_id)
    if not idx:
        return jsonify({"error": "Index not loaded"}), 404

    data = request.get_json(silent=True)
    if not data or 'documents' not in data:
        return jsonify({"error": "Request must include 'documents' array"}), 400

    documents = data['documents']
    if not isinstance(documents, list):
        return jsonify({"error": "'documents' must be an array"}), 400

    idx.add_documents(documents)
    _save_index_meta(idx)

    return jsonify({"status": "ok", "document_count": idx.docstore.count})


@app.route('/indexes/<index_id>/delete', methods=['POST'])
def delete_index(index_id):
    if index_id in _index_registry:
        del _index_registry[index_id]

    meta_path = os.path.join(INDEX_STORE, f"{index_id}.meta.json")
    if os.path.isfile(meta_path):
        os.remove(meta_path)

    return redirect(url_for('list_indexes'))


@app.route('/api/v1/indexes/restore', methods=['POST'])
def api_restore_index():
    """API endpoint to restore a vector index from serialized bytes."""
    content_type = request.content_type or ''

    if 'application/json' in content_type:
        data = request.get_json(silent=True)
        if not data or 'serialized' not in data:
            return jsonify({"error": "Missing 'serialized' field"}), 400
        try:
            serialized = base64.b64decode(data['serialized'])
        except Exception:
            return jsonify({"error": "Invalid base64 encoding"}), 400
    elif 'application/octet-stream' in content_type:
        serialized = request.get_data()
        if not serialized:
            return jsonify({"error": "Empty request body"}), 400
    else:
        return jsonify({"error": "Unsupported content type"}), 415

    try:
        idx = VectorIndex.restore_from_bytes(serialized)
        _index_registry[idx.index_id] = idx
        _save_index_meta(idx)
        return jsonify({"status": "ok", "index": idx.info()})
    except Exception:
        return jsonify({"error": "Failed to restore index from provided data"}), 400


@app.route('/docs')
def api_docs():
    return render_template('api_docs.html')
