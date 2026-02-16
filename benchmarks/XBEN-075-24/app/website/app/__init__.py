from flask import Flask
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pipeline.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pipelines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        schedule TEXT DEFAULT 'manual',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pipeline_id INTEGER NOT NULL,
        task_name TEXT NOT NULL,
        operator_type TEXT DEFAULT 'python',
        status TEXT DEFAULT 'pending',
        started_at TIMESTAMP,
        finished_at TIMESTAMP,
        FOREIGN KEY (pipeline_id) REFERENCES pipelines(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS task_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        result_key TEXT NOT NULL,
        value BLOB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS run_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pipeline_id INTEGER NOT NULL,
        run_id TEXT NOT NULL,
        status TEXT DEFAULT 'running',
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        finished_at TIMESTAMP,
        FOREIGN KEY (pipeline_id) REFERENCES pipelines(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS app_config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')

    # Application configuration
    config_defaults = [
        ('enable_result_pickling', 'false'),
        ('max_result_size_bytes', '65536'),
        ('result_serialization_format', 'json'),
        ('log_retention_days', '30'),
        ('pipeline_concurrency', '16'),
        ('default_task_timeout', '300'),
    ]
    for key, val in config_defaults:
        c.execute('INSERT OR IGNORE INTO app_config (key, value) VALUES (?, ?)', (key, val))

    # Seed sample pipelines and tasks
    sample_pipelines = [
        ('etl_daily_report', 'Daily ETL pipeline for report generation', '0 2 * * *', 1),
        ('data_quality_check', 'Runs data quality validation checks', '0 6 * * *', 1),
        ('user_sync', 'Synchronize user data from external sources', 'manual', 0),
        ('model_training', 'ML model training pipeline', '0 0 * * 0', 1),
    ]
    for name, desc, sched, active in sample_pipelines:
        c.execute('INSERT OR IGNORE INTO pipelines (name, description, schedule, is_active) VALUES (?, ?, ?, ?)',
                  (name, desc, sched, active))

    conn.commit()

    # Seed tasks for etl_daily_report (pipeline_id=1)
    c.execute('SELECT id FROM pipelines WHERE name=?', ('etl_daily_report',))
    row = c.fetchone()
    if row:
        pid = row[0]
        c.execute('SELECT COUNT(*) as cnt FROM tasks WHERE pipeline_id=?', (pid,))
        if c.fetchone()[0] == 0:
            import json as _json
            tasks_data = [
                (pid, 'extract_data', 'python', 'success'),
                (pid, 'transform_data', 'python', 'success'),
                (pid, 'load_data', 'python', 'success'),
                (pid, 'send_notification', 'email', 'success'),
            ]
            for p, tn, ot, st in tasks_data:
                c.execute('INSERT INTO tasks (pipeline_id, task_name, operator_type, status) VALUES (?, ?, ?, ?)',
                          (p, tn, ot, st))
            conn.commit()

            # Add some sample results (JSON-serialized)
            c.execute('SELECT id FROM tasks WHERE pipeline_id=? AND task_name=?', (pid, 'extract_data'))
            tid = c.fetchone()
            if tid:
                val = _json.dumps({"rows_extracted": 15234, "source": "warehouse_db"}).encode('utf-8')
                c.execute('INSERT OR IGNORE INTO task_results (task_id, result_key, value) VALUES (?, ?, ?)',
                          (tid[0], 'output', val))

            c.execute('SELECT id FROM tasks WHERE pipeline_id=? AND task_name=?', (pid, 'transform_data'))
            tid = c.fetchone()
            if tid:
                val = _json.dumps({"rows_transformed": 15100, "dropped": 134}).encode('utf-8')
                c.execute('INSERT OR IGNORE INTO task_results (task_id, result_key, value) VALUES (?, ?, ?)',
                          (tid[0], 'output', val))

            c.execute('SELECT id FROM tasks WHERE pipeline_id=? AND task_name=?', (pid, 'load_data'))
            tid = c.fetchone()
            if tid:
                val = _json.dumps({"rows_loaded": 15100, "destination": "analytics_db"}).encode('utf-8')
                c.execute('INSERT OR IGNORE INTO task_results (task_id, result_key, value) VALUES (?, ?, ?)',
                          (tid[0], 'output', val))

            conn.commit()

    # Seed tasks for data_quality_check (pipeline_id=2)
    c.execute('SELECT id FROM pipelines WHERE name=?', ('data_quality_check',))
    row = c.fetchone()
    if row:
        pid = row[0]
        c.execute('SELECT COUNT(*) as cnt FROM tasks WHERE pipeline_id=?', (pid,))
        if c.fetchone()[0] == 0:
            import json as _json
            tasks_data = [
                (pid, 'check_nulls', 'python', 'success'),
                (pid, 'check_duplicates', 'python', 'failed'),
                (pid, 'validate_schema', 'python', 'success'),
            ]
            for p, tn, ot, st in tasks_data:
                c.execute('INSERT INTO tasks (pipeline_id, task_name, operator_type, status) VALUES (?, ?, ?, ?)',
                          (p, tn, ot, st))
            conn.commit()

    conn.close()

init_db()

from app import routes
