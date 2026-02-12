"""REST API endpoints for Airflow - XCom, DAGs, Task Instances."""

import json
import base64
import datetime
import logging

from flask import request, jsonify
from app import app
from app.database import get_db
from app.models import XCom, DagModel, DagRun, TaskInstance

log = logging.getLogger(__name__)


@app.route('/api/v1/dags', methods=['GET'])
def api_list_dags():
    """List all DAGs."""
    db = get_db()
    rows = db.execute("SELECT * FROM dag ORDER BY dag_id").fetchall()
    db.close()
    dags = [DagModel(r).to_dict() for r in rows]
    return jsonify({'dags': dags, 'total_entries': len(dags)})


@app.route('/api/v1/dags/<dag_id>', methods=['GET'])
def api_get_dag(dag_id):
    """Get a specific DAG."""
    db = get_db()
    row = db.execute("SELECT * FROM dag WHERE dag_id = ?", (dag_id,)).fetchone()
    db.close()
    if not row:
        return jsonify({'detail': f'DAG with dag_id={dag_id!r} not found', 'status': 404, 'title': 'Not Found'}), 404
    return jsonify(DagModel(row).to_dict())


@app.route('/api/v1/dags/<dag_id>/dagRuns', methods=['GET'])
def api_list_dag_runs(dag_id):
    """List DAG runs for a specific DAG."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM dag_run WHERE dag_id = ? ORDER BY execution_date DESC",
        (dag_id,)
    ).fetchall()
    db.close()
    runs = [DagRun(r).to_dict() for r in rows]
    return jsonify({'dag_runs': runs, 'total_entries': len(runs)})


@app.route('/api/v1/dags/<dag_id>/dagRuns/<run_id>/taskInstances', methods=['GET'])
def api_list_task_instances(dag_id, run_id):
    """List task instances for a specific DAG run."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM task_instance WHERE dag_id = ? AND run_id = ? ORDER BY start_date",
        (dag_id, run_id)
    ).fetchall()
    db.close()
    tasks = [TaskInstance(r).to_dict() for r in rows]
    return jsonify({'task_instances': tasks, 'total_entries': len(tasks)})


@app.route('/api/v1/dags/<dag_id>/dagRuns/<run_id>/taskInstances/<task_id>/xcomEntries', methods=['GET'])
def api_list_xcom_entries(dag_id, run_id, task_id):
    """List XCom entries for a specific task instance."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM xcom WHERE dag_id = ? AND run_id = ? AND task_id = ? ORDER BY timestamp",
        (dag_id, run_id, task_id)
    ).fetchall()
    db.close()
    entries = []
    for r in rows:
        xcom = XCom(r)
        entries.append(xcom.to_dict())
    return jsonify({'xcom_entries': entries, 'total_entries': len(entries)})


@app.route('/api/v1/dags/<dag_id>/dagRuns/<run_id>/taskInstances/<task_id>/xcomEntries/<key>', methods=['GET'])
def api_get_xcom_entry(dag_id, run_id, task_id, key):
    """Get a specific XCom entry - triggers deserialization."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM xcom WHERE dag_id = ? AND run_id = ? AND task_id = ? AND key = ?",
        (dag_id, run_id, task_id, key)
    ).fetchone()
    db.close()
    if not row:
        return jsonify({
            'detail': f'XCom entry not found for dag_id={dag_id!r}, run_id={run_id!r}, task_id={task_id!r}, key={key!r}',
            'status': 404,
            'title': 'Not Found'
        }), 404
    xcom = XCom(row)
    return jsonify(xcom.to_dict())


@app.route('/api/v1/xcom', methods=['POST'])
def api_push_xcom():
    """Push an XCom value (used by tasks to store cross-communication data).

    Accepts JSON with fields: dag_id, task_id, run_id, execution_date, key, value
    The value field can be any JSON-serializable object.

    Alternatively, set raw_bytes=true and provide value as base64-encoded bytes
    for binary data compatibility (legacy support).
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'detail': 'Request body must be valid JSON', 'status': 400, 'title': 'Bad Request'}), 400

    required = ['dag_id', 'task_id', 'key', 'value']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({
            'detail': f'Missing required fields: {missing}',
            'status': 400,
            'title': 'Bad Request'
        }), 400

    dag_id = data['dag_id']
    task_id = data['task_id']
    key = data['key']
    run_id = data.get('run_id', 'manual__' + datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'))
    execution_date = data.get('execution_date', datetime.datetime.utcnow().isoformat())

    # Check that referenced DAG exists
    db = get_db()
    dag = db.execute("SELECT * FROM dag WHERE dag_id = ?", (dag_id,)).fetchone()
    if not dag:
        db.close()
        return jsonify({'detail': f'DAG {dag_id!r} not found', 'status': 404, 'title': 'Not Found'}), 404

    if data.get('raw_bytes'):
        # Legacy binary support: value is base64-encoded bytes
        try:
            value_bytes = base64.b64decode(data['value'])
        except Exception:
            db.close()
            return jsonify({'detail': 'Invalid base64 in value field', 'status': 400, 'title': 'Bad Request'}), 400
    else:
        # Standard JSON serialization
        value_bytes = json.dumps(data['value']).encode('utf-8')

    timestamp = datetime.datetime.utcnow().isoformat()

    db.execute(
        "INSERT INTO xcom (key, value, timestamp, execution_date, task_id, dag_id, run_id) VALUES (?,?,?,?,?,?,?)",
        (key, value_bytes, timestamp, execution_date, task_id, dag_id, run_id)
    )
    db.commit()
    db.close()

    return jsonify({
        'key': key,
        'dag_id': dag_id,
        'task_id': task_id,
        'run_id': run_id,
        'execution_date': execution_date,
        'timestamp': timestamp,
    }), 201


@app.route('/api/v1/config', methods=['GET'])
def api_get_config():
    """Get selected Airflow configuration (non-sensitive)."""
    return jsonify({
        'sections': {
            'core': {
                'executor': app.config.get('EXECUTOR', 'SequentialExecutor'),
                'enable_xcom_pickling': str(app.config.get('ENABLE_XCOM_PICKLING', False)),
                'dags_folder': '/opt/airflow/dags',
                'load_examples': 'False',
            },
            'webserver': {
                'web_server_port': '8080',
                'expose_config': 'non-sensitive-only',
                'rbac': 'True',
            },
            'scheduler': {
                'min_file_process_interval': '30',
                'dag_dir_list_interval': '300',
            },
        }
    })


@app.route('/api/v1/health', methods=['GET'])
def api_health():
    """Health check endpoint."""
    db = get_db()
    try:
        db.execute("SELECT 1")
        db_status = 'healthy'
    except Exception:
        db_status = 'unhealthy'
    finally:
        db.close()
    return jsonify({
        'metadatabase': {'status': db_status},
        'scheduler': {'status': 'healthy', 'latest_scheduler_heartbeat': datetime.datetime.utcnow().isoformat()},
    })


@app.route('/api/v1/connections', methods=['GET'])
def api_list_connections():
    """List connections (passwords masked)."""
    db = get_db()
    rows = db.execute("SELECT * FROM connection ORDER BY conn_id").fetchall()
    db.close()
    conns = []
    for r in rows:
        conns.append({
            'conn_id': r['conn_id'],
            'conn_type': r['conn_type'],
            'host': r['host'],
            'schema': r['schema_name'],
            'login': r['login'],
            'port': r['port'],
            'password': '***' if r['password'] else None,
        })
    return jsonify({'connections': conns, 'total_entries': len(conns)})


@app.route('/api/v1/variables', methods=['GET'])
def api_list_variables():
    """List variables."""
    db = get_db()
    rows = db.execute("SELECT * FROM variable ORDER BY key").fetchall()
    db.close()
    variables = [{'key': r['key'], 'value': r['val']} for r in rows]
    return jsonify({'variables': variables, 'total_entries': len(variables)})
