from flask import (
    render_template, redirect, url_for,
    request, jsonify, abort
)
import logging

from app import app, get_db
from app.models import TaskResult, AppConfiguration

logger = logging.getLogger(__name__)


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    conn = get_db()
    pipelines = conn.execute(
        'SELECT p.*, COUNT(t.id) as task_count FROM pipelines p '
        'LEFT JOIN tasks t ON p.id = t.pipeline_id '
        'GROUP BY p.id ORDER BY p.created_at DESC'
    ).fetchall()
    recent_logs = conn.execute(
        'SELECT rl.*, p.name as pipeline_name FROM run_logs rl '
        'JOIN pipelines p ON rl.pipeline_id = p.id '
        'ORDER BY rl.started_at DESC LIMIT 10'
    ).fetchall()
    conn.close()
    return render_template('dashboard.html', pipelines=pipelines, recent_logs=recent_logs)


@app.route('/pipeline/<int:pipeline_id>')
def pipeline_detail(pipeline_id):
    conn = get_db()
    pipeline = conn.execute('SELECT * FROM pipelines WHERE id=?', (pipeline_id,)).fetchone()
    if not pipeline:
        conn.close()
        abort(404)
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE pipeline_id=? ORDER BY id', (pipeline_id,)
    ).fetchall()
    logs = conn.execute(
        'SELECT * FROM run_logs WHERE pipeline_id=? ORDER BY started_at DESC LIMIT 20',
        (pipeline_id,)
    ).fetchall()
    conn.close()
    return render_template('pipeline_detail.html', pipeline=pipeline, tasks=tasks, logs=logs)


@app.route('/pipeline/<int:pipeline_id>/task/<int:task_id>')
def task_detail(pipeline_id, task_id):
    conn = get_db()
    pipeline = conn.execute('SELECT * FROM pipelines WHERE id=?', (pipeline_id,)).fetchone()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id=? AND pipeline_id=?', (task_id, pipeline_id)
    ).fetchone()
    if not pipeline or not task:
        conn.close()
        abort(404)
    rows = conn.execute(
        'SELECT * FROM task_results WHERE task_id=? ORDER BY created_at DESC', (task_id,)
    ).fetchall()
    conn.close()

    results = []
    for row in rows:
        try:
            display_value = TaskResult.orm_deserialize_value(row['value'])
        except Exception:
            display_value = '<binary data>'
        results.append({
            'result_key': row['result_key'],
            'value': display_value,
            'created_at': row['created_at'],
        })

    return render_template('task_detail.html', pipeline=pipeline, task=task, results=results)


@app.route('/api/v1/pipelines', methods=['GET'])
def api_list_pipelines():
    conn = get_db()
    pipelines = conn.execute('SELECT * FROM pipelines ORDER BY id').fetchall()
    conn.close()
    return jsonify({
        'pipelines': [dict(p) for p in pipelines],
        'total_entries': len(pipelines)
    })


@app.route('/api/v1/pipelines/<int:pipeline_id>', methods=['GET'])
def api_get_pipeline(pipeline_id):
    conn = get_db()
    pipeline = conn.execute('SELECT * FROM pipelines WHERE id=?', (pipeline_id,)).fetchone()
    if not pipeline:
        conn.close()
        return jsonify({'error': 'Pipeline not found'}), 404
    tasks = conn.execute('SELECT * FROM tasks WHERE pipeline_id=?', (pipeline_id,)).fetchall()
    conn.close()
    return jsonify({
        'pipeline': dict(pipeline),
        'tasks': [dict(t) for t in tasks]
    })


@app.route('/api/v1/pipelines/<int:pipeline_id>/tasks/<int:task_id>/results', methods=['GET'])
def api_get_task_results(pipeline_id, task_id):
    conn = get_db()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id=? AND pipeline_id=?', (task_id, pipeline_id)
    ).fetchone()
    if not task:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    result_key = request.args.get('key')
    if result_key:
        rows = conn.execute(
            'SELECT * FROM task_results WHERE task_id=? AND result_key=?',
            (task_id, result_key)
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT * FROM task_results WHERE task_id=? ORDER BY created_at DESC',
            (task_id,)
        ).fetchall()
    conn.close()

    entries = []
    for row in rows:
        entry = {
            'id': row['id'],
            'task_id': row['task_id'],
            'result_key': row['result_key'],
            'created_at': row['created_at'],
        }
        try:
            val = TaskResult.deserialize_value(row['value'])
            if isinstance(val, bytes):
                val = val.decode('utf-8', errors='replace')
            entry['value'] = val
        except Exception:
            entry['value'] = None
        entries.append(entry)

    return jsonify({
        'task_results': entries,
        'total_entries': len(entries)
    })


@app.route('/api/v1/pipelines/<int:pipeline_id>/tasks/<int:task_id>/results', methods=['POST'])
def api_set_task_result(pipeline_id, task_id):
    conn = get_db()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id=? AND pipeline_id=?', (task_id, pipeline_id)
    ).fetchone()
    if not task:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    content_type = request.content_type or ''

    if 'application/octet-stream' in content_type:
        result_key = request.args.get('key', 'output')
        raw_data = request.get_data()
        max_size = int(AppConfiguration.get_string('max_result_size_bytes', '65536'))
        if len(raw_data) > max_size:
            conn.close()
            return jsonify({'error': 'Result value exceeds maximum size'}), 413

        conn.execute(
            'INSERT INTO task_results (task_id, result_key, value) VALUES (?, ?, ?)',
            (task_id, result_key, raw_data)
        )
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok', 'message': 'Task result stored'}), 201

    elif 'application/json' in content_type:
        data = request.get_json(silent=True)
        if not data or 'key' not in data:
            conn.close()
            return jsonify({'error': 'Missing required field: key'}), 400

        result_key = data['key']
        value = data.get('value', None)

        try:
            serialized = TaskResult.serialize_value(value)
        except (ValueError, TypeError):
            conn.close()
            return jsonify({'error': 'Failed to serialize value'}), 400

        max_size = int(AppConfiguration.get_string('max_result_size_bytes', '65536'))
        if len(serialized) > max_size:
            conn.close()
            return jsonify({'error': 'Result value exceeds maximum size'}), 413

        conn.execute(
            'INSERT INTO task_results (task_id, result_key, value) VALUES (?, ?, ?)',
            (task_id, result_key, serialized)
        )
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok', 'message': 'Task result stored'}), 201
    else:
        conn.close()
        return jsonify({'error': 'Unsupported content type'}), 415


@app.route('/api/v1/config', methods=['GET'])
def api_get_config():
    conn = get_db()
    rows = conn.execute('SELECT key, value FROM app_config').fetchall()
    conn.close()
    config = {row['key']: row['value'] for row in rows}
    return jsonify({'config': config})


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})
