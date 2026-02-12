import sqlite3
import os
import json
import datetime

DB_PATH = '/var/lib/airflow/airflow.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dag (
            dag_id TEXT PRIMARY KEY,
            description TEXT,
            schedule_interval TEXT,
            is_paused INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            last_parsed_time TEXT,
            fileloc TEXT,
            owners TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dag_run (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dag_id TEXT NOT NULL,
            run_id TEXT NOT NULL,
            execution_date TEXT NOT NULL,
            state TEXT DEFAULT 'running',
            start_date TEXT,
            end_date TEXT,
            conf TEXT,
            FOREIGN KEY (dag_id) REFERENCES dag(dag_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_instance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            dag_id TEXT NOT NULL,
            run_id TEXT NOT NULL,
            execution_date TEXT NOT NULL,
            state TEXT DEFAULT 'success',
            start_date TEXT,
            end_date TEXT,
            operator TEXT,
            try_number INTEGER DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS xcom (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            value BLOB,
            timestamp TEXT NOT NULL,
            execution_date TEXT NOT NULL,
            task_id TEXT NOT NULL,
            dag_id TEXT NOT NULL,
            run_id TEXT DEFAULT ''
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS connection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conn_id TEXT UNIQUE NOT NULL,
            conn_type TEXT NOT NULL,
            host TEXT,
            schema_name TEXT,
            login TEXT,
            password TEXT,
            port INTEGER,
            extra TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS variable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            val TEXT,
            is_encrypted INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ab_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            first_name TEXT,
            last_name TEXT,
            active INTEGER DEFAULT 1,
            last_login TEXT
        )
    ''')

    # Seed realistic data
    _seed_data(cursor)

    conn.commit()
    conn.close()


def _seed_data(cursor):
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM dag")
    if cursor.fetchone()[0] > 0:
        return

    now = datetime.datetime.utcnow().isoformat()
    yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat()
    two_days_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=2)).isoformat()

    # DAGs
    dags = [
        ('etl_pipeline', 'Main ETL pipeline for data warehouse', '0 2 * * *', 0, 1, now, '/opt/airflow/dags/etl_pipeline.py', 'data_team'),
        ('ml_training', 'ML model training pipeline', '0 6 * * 1', 0, 1, now, '/opt/airflow/dags/ml_training.py', 'ml_team'),
        ('data_quality_checks', 'Data quality validation', '30 3 * * *', 0, 1, now, '/opt/airflow/dags/data_quality_checks.py', 'data_team'),
        ('report_generation', 'Weekly report generation', '0 8 * * 5', 1, 1, now, '/opt/airflow/dags/report_generation.py', 'analytics'),
        ('log_cleanup', 'Clean up old log files', '0 0 * * 0', 0, 1, now, '/opt/airflow/dags/log_cleanup.py', 'platform'),
        ('user_sync', 'Sync user data from external API', '*/30 * * * *', 0, 1, now, '/opt/airflow/dags/user_sync.py', 'platform'),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO dag VALUES (?,?,?,?,?,?,?,?)", dags
    )

    # DAG runs
    dag_runs = [
        ('etl_pipeline', 'scheduled__2024-01-15T02:00:00', '2024-01-15T02:00:00', 'success', '2024-01-15T02:00:05', '2024-01-15T02:45:30', None),
        ('etl_pipeline', 'scheduled__2024-01-16T02:00:00', '2024-01-16T02:00:00', 'success', '2024-01-16T02:00:03', '2024-01-16T02:42:15', None),
        ('etl_pipeline', 'scheduled__2024-01-17T02:00:00', '2024-01-17T02:00:00', 'running', '2024-01-17T02:00:02', None, None),
        ('ml_training', 'scheduled__2024-01-15T06:00:00', '2024-01-15T06:00:00', 'success', '2024-01-15T06:00:10', '2024-01-15T08:15:42', None),
        ('data_quality_checks', 'scheduled__2024-01-16T03:30:00', '2024-01-16T03:30:00', 'success', '2024-01-16T03:30:01', '2024-01-16T03:35:22', None),
        ('data_quality_checks', 'scheduled__2024-01-17T03:30:00', '2024-01-17T03:30:00', 'failed', '2024-01-17T03:30:02', '2024-01-17T03:33:10', None),
        ('user_sync', 'scheduled__2024-01-17T12:00:00', '2024-01-17T12:00:00', 'success', '2024-01-17T12:00:01', '2024-01-17T12:02:30', None),
        ('user_sync', 'scheduled__2024-01-17T12:30:00', '2024-01-17T12:30:00', 'success', '2024-01-17T12:30:01', '2024-01-17T12:32:15', None),
        ('log_cleanup', 'scheduled__2024-01-14T00:00:00', '2024-01-14T00:00:00', 'success', '2024-01-14T00:00:05', '2024-01-14T00:05:30', None),
    ]
    for dr in dag_runs:
        cursor.execute(
            "INSERT INTO dag_run (dag_id, run_id, execution_date, state, start_date, end_date, conf) VALUES (?,?,?,?,?,?,?)",
            dr
        )

    # Task instances
    tasks = [
        ('extract_data', 'etl_pipeline', 'scheduled__2024-01-16T02:00:00', '2024-01-16T02:00:00', 'success', '2024-01-16T02:00:05', '2024-01-16T02:15:30', 'PythonOperator', 1),
        ('transform_data', 'etl_pipeline', 'scheduled__2024-01-16T02:00:00', '2024-01-16T02:00:00', 'success', '2024-01-16T02:15:35', '2024-01-16T02:30:20', 'PythonOperator', 1),
        ('load_data', 'etl_pipeline', 'scheduled__2024-01-16T02:00:00', '2024-01-16T02:00:00', 'success', '2024-01-16T02:30:25', '2024-01-16T02:42:15', 'PythonOperator', 1),
        ('validate_schema', 'etl_pipeline', 'scheduled__2024-01-16T02:00:00', '2024-01-16T02:00:00', 'success', '2024-01-16T02:00:05', '2024-01-16T02:05:10', 'PythonOperator', 1),
        ('prepare_features', 'ml_training', 'scheduled__2024-01-15T06:00:00', '2024-01-15T06:00:00', 'success', '2024-01-15T06:00:15', '2024-01-15T06:30:00', 'PythonOperator', 1),
        ('train_model', 'ml_training', 'scheduled__2024-01-15T06:00:00', '2024-01-15T06:00:00', 'success', '2024-01-15T06:30:05', '2024-01-15T07:45:30', 'PythonOperator', 1),
        ('evaluate_model', 'ml_training', 'scheduled__2024-01-15T06:00:00', '2024-01-15T06:00:00', 'success', '2024-01-15T07:45:35', '2024-01-15T08:15:42', 'PythonOperator', 1),
        ('check_nulls', 'data_quality_checks', 'scheduled__2024-01-17T03:30:00', '2024-01-17T03:30:00', 'failed', '2024-01-17T03:30:05', '2024-01-17T03:33:10', 'PythonOperator', 2),
        ('check_duplicates', 'data_quality_checks', 'scheduled__2024-01-17T03:30:00', '2024-01-17T03:30:00', 'success', '2024-01-17T03:30:03', '2024-01-17T03:31:20', 'PythonOperator', 1),
        ('fetch_users', 'user_sync', 'scheduled__2024-01-17T12:30:00', '2024-01-17T12:30:00', 'success', '2024-01-17T12:30:03', '2024-01-17T12:31:15', 'PythonOperator', 1),
        ('update_database', 'user_sync', 'scheduled__2024-01-17T12:30:00', '2024-01-17T12:30:00', 'success', '2024-01-17T12:31:20', '2024-01-17T12:32:15', 'PythonOperator', 1),
        ('cleanup_logs', 'log_cleanup', 'scheduled__2024-01-14T00:00:00', '2024-01-14T00:00:00', 'success', '2024-01-14T00:00:10', '2024-01-14T00:05:30', 'BashOperator', 1),
    ]
    for t in tasks:
        cursor.execute(
            "INSERT INTO task_instance (task_id, dag_id, run_id, execution_date, state, start_date, end_date, operator, try_number) VALUES (?,?,?,?,?,?,?,?,?)",
            t
        )

    # XCom entries (legitimate JSON values)
    xcom_entries = [
        ('return_value', json.dumps({"rows_extracted": 15234, "source": "postgres_main"}).encode('utf-8'),
         '2024-01-16T02:15:30', '2024-01-16T02:00:00', 'extract_data', 'etl_pipeline', 'scheduled__2024-01-16T02:00:00'),
        ('return_value', json.dumps({"rows_transformed": 15100, "dropped": 134}).encode('utf-8'),
         '2024-01-16T02:30:20', '2024-01-16T02:00:00', 'transform_data', 'etl_pipeline', 'scheduled__2024-01-16T02:00:00'),
        ('return_value', json.dumps({"rows_loaded": 15100, "table": "warehouse.fact_events"}).encode('utf-8'),
         '2024-01-16T02:42:15', '2024-01-16T02:00:00', 'load_data', 'etl_pipeline', 'scheduled__2024-01-16T02:00:00'),
        ('schema_version', json.dumps("v2.3.1").encode('utf-8'),
         '2024-01-16T02:05:10', '2024-01-16T02:00:00', 'validate_schema', 'etl_pipeline', 'scheduled__2024-01-16T02:00:00'),
        ('return_value', json.dumps({"accuracy": 0.943, "f1_score": 0.921, "model_path": "/models/v42"}).encode('utf-8'),
         '2024-01-15T08:15:42', '2024-01-15T06:00:00', 'evaluate_model', 'ml_training', 'scheduled__2024-01-15T06:00:00'),
        ('feature_count', json.dumps(47).encode('utf-8'),
         '2024-01-15T06:30:00', '2024-01-15T06:00:00', 'prepare_features', 'ml_training', 'scheduled__2024-01-15T06:00:00'),
        ('return_value', json.dumps({"null_pct": 12.5, "threshold": 5.0, "status": "FAIL"}).encode('utf-8'),
         '2024-01-17T03:33:10', '2024-01-17T03:30:00', 'check_nulls', 'data_quality_checks', 'scheduled__2024-01-17T03:30:00'),
        ('return_value', json.dumps({"duplicates_found": 0, "status": "PASS"}).encode('utf-8'),
         '2024-01-17T03:31:20', '2024-01-17T03:30:00', 'check_duplicates', 'data_quality_checks', 'scheduled__2024-01-17T03:30:00'),
        ('return_value', json.dumps({"users_synced": 342, "new_users": 12}).encode('utf-8'),
         '2024-01-17T12:32:15', '2024-01-17T12:30:00', 'update_database', 'user_sync', 'scheduled__2024-01-17T12:30:00'),
        ('return_value', json.dumps({"files_removed": 156, "space_freed_mb": 2340}).encode('utf-8'),
         '2024-01-14T00:05:30', '2024-01-14T00:00:00', 'cleanup_logs', 'log_cleanup', 'scheduled__2024-01-14T00:00:00'),
    ]
    for xc in xcom_entries:
        cursor.execute(
            "INSERT INTO xcom (key, value, timestamp, execution_date, task_id, dag_id, run_id) VALUES (?,?,?,?,?,?,?)",
            xc
        )

    # Connections
    connections = [
        ('postgres_main', 'postgres', 'db-main.internal.corp', 'analytics', 'etl_user', '***', 5432, '{"sslmode": "require"}'),
        ('redis_cache', 'redis', 'redis.internal.corp', None, None, '***', 6379, None),
        ('s3_data_lake', 'aws', None, None, 'AKIA***', '***', None, '{"region_name": "us-east-1", "bucket": "data-lake-prod"}'),
        ('slack_alerts', 'http', 'hooks.slack.com', None, None, '***', 443, '{"webhook_path": "/services/T00/B00/xxx"}'),
    ]
    for c in connections:
        cursor.execute(
            "INSERT OR IGNORE INTO connection (conn_id, conn_type, host, schema_name, login, password, port, extra) VALUES (?,?,?,?,?,?,?,?)",
            c
        )

    # Variables
    variables = [
        ('environment', 'production', 0),
        ('data_retention_days', '90', 0),
        ('alert_email', 'data-alerts@company.com', 0),
        ('model_registry_url', 'https://mlflow.internal.corp', 0),
    ]
    for v in variables:
        cursor.execute(
            "INSERT OR IGNORE INTO variable (key, val, is_encrypted) VALUES (?,?,?)",
            v
        )

    # Users
    users = [
        ('admin', 'admin@company.com', 'Admin', 'User', 1, now),
        ('data_engineer', 'de@company.com', 'Data', 'Engineer', 1, yesterday),
        ('ml_engineer', 'ml@company.com', 'ML', 'Engineer', 1, two_days_ago),
        ('analyst', 'analyst@company.com', 'Data', 'Analyst', 1, yesterday),
    ]
    for u in users:
        cursor.execute(
            "INSERT OR IGNORE INTO ab_user (username, email, first_name, last_name, active, last_login) VALUES (?,?,?,?,?,?)",
            u
        )
