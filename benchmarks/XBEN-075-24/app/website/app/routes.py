"""Web UI routes for Airflow dashboard."""

from flask import render_template, redirect, url_for, request, jsonify
from app import app
from app.database import get_db
from app.models import DagModel, DagRun, TaskInstance, XCom
import logging

log = logging.getLogger(__name__)


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
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
    return redirect(url_for('dags_list'))


@app.route('/home')
def dags_list():
    db = get_db()
    rows = db.execute("SELECT * FROM dag ORDER BY dag_id").fetchall()
    dags = [DagModel(r) for r in rows]

    # Get latest run state for each DAG
    dag_stats = {}
    for dag in dags:
        latest_run = db.execute(
            "SELECT state FROM dag_run WHERE dag_id = ? ORDER BY execution_date DESC LIMIT 1",
            (dag.dag_id,)
        ).fetchone()
        run_count = db.execute(
            "SELECT COUNT(*) FROM dag_run WHERE dag_id = ?",
            (dag.dag_id,)
        ).fetchone()[0]
        dag_stats[dag.dag_id] = {
            'latest_state': latest_run['state'] if latest_run else None,
            'run_count': run_count
        }

    db.close()
    return render_template('dags.html', dags=dags, dag_stats=dag_stats)


@app.route('/dags/<dag_id>')
def dag_detail(dag_id):
    db = get_db()
    dag_row = db.execute("SELECT * FROM dag WHERE dag_id = ?", (dag_id,)).fetchone()
    if not dag_row:
        db.close()
        return render_template('error.html', code=404, message=f'DAG "{dag_id}" not found'), 404

    dag = DagModel(dag_row)
    runs_rows = db.execute(
        "SELECT * FROM dag_run WHERE dag_id = ? ORDER BY execution_date DESC LIMIT 25",
        (dag_id,)
    ).fetchall()
    runs = [DagRun(r) for r in runs_rows]
    db.close()
    return render_template('dag_detail.html', dag=dag, runs=runs)


@app.route('/dags/<dag_id>/runs/<run_id>')
def dag_run_detail(dag_id, run_id):
    db = get_db()
    dag_row = db.execute("SELECT * FROM dag WHERE dag_id = ?", (dag_id,)).fetchone()
    if not dag_row:
        db.close()
        return render_template('error.html', code=404, message=f'DAG "{dag_id}" not found'), 404

    run_row = db.execute(
        "SELECT * FROM dag_run WHERE dag_id = ? AND run_id = ?",
        (dag_id, run_id)
    ).fetchone()
    if not run_row:
        db.close()
        return render_template('error.html', code=404, message=f'Run "{run_id}" not found'), 404

    dag = DagModel(dag_row)
    run = DagRun(run_row)

    task_rows = db.execute(
        "SELECT * FROM task_instance WHERE dag_id = ? AND run_id = ? ORDER BY start_date",
        (dag_id, run_id)
    ).fetchall()
    tasks = [TaskInstance(r) for r in task_rows]

    db.close()
    return render_template('dag_run.html', dag=dag, run=run, tasks=tasks)


@app.route('/dags/<dag_id>/runs/<run_id>/tasks/<task_id>/xcom')
def task_xcom(dag_id, run_id, task_id):
    db = get_db()
    xcom_rows = db.execute(
        "SELECT * FROM xcom WHERE dag_id = ? AND run_id = ? AND task_id = ? ORDER BY timestamp",
        (dag_id, run_id, task_id)
    ).fetchall()
    xcoms = []
    for r in xcom_rows:
        xcom = XCom(r)
        xcoms.append(xcom.to_dict())
    db.close()
    return render_template('xcom.html', xcoms=xcoms, dag_id=dag_id, run_id=run_id, task_id=task_id)


@app.route('/ping')
def ping():
    return 'OK', 200
