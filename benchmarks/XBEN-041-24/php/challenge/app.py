from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import hashlib
import time

app = Flask(__name__)
app.secret_key = 'workflow-manager-secret-key-2024'

# Simulated DAGs (workflows)
DAGS = {
    'etl_pipeline': {
        'name': 'ETL Data Pipeline',
        'description': 'Extract, transform, and load data from sources',
        'schedule': '0 0 * * *',
        'active': True
    },
    'report_generator': {
        'name': 'Daily Report Generator',
        'description': 'Generate daily business reports',
        'schedule': '0 6 * * *',
        'active': True
    },
    'data_cleanup': {
        'name': 'Data Cleanup Job',
        'description': 'Clean up stale data from databases',
        'schedule': '0 2 * * 0',
        'active': False
    }
}

# Simple user database
USERS = {
    'operator': hashlib.sha256('workflow2024'.encode()).hexdigest(),
    'admin': hashlib.sha256('supersecretadminpass'.encode()).hexdigest()
}

# Store triggered runs
triggered_runs = {}

def get_logs_base_path():
    return os.path.join(os.path.dirname(__file__), 'logs', 'dag_runs')

def ensure_logs_dir():
    logs_path = get_logs_base_path()
    os.makedirs(logs_path, exist_ok=True)
    return logs_path

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template_string(HOME_TEMPLATE, dags=DAGS, user=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username in USERS and USERS[username] == password_hash:
            session['user'] = username
            return redirect(url_for('index'))
        error = 'Invalid credentials'
    
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dags/<dag_id>')
def dag_detail(dag_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if dag_id not in DAGS:
        return "DAG not found", 404
    
    dag = DAGS[dag_id]
    runs = [r for r in triggered_runs.values() if r['dag_id'] == dag_id]
    return render_template_string(DAG_DETAIL_TEMPLATE, dag=dag, dag_id=dag_id, runs=runs, user=session.get('user'))

@app.route('/dags/<dag_id>/trigger', methods=['GET', 'POST'])
def trigger_dag(dag_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if dag_id not in DAGS:
        return "DAG not found", 404
    
    if request.method == 'POST':
        # Get run_id from form - VULNERABILITY: no validation on run_id
        run_id = request.form.get('run_id', '')
        
        if not run_id:
            run_id = f"manual__{int(time.time())}"
        
        # Create the run entry
        triggered_runs[run_id] = {
            'dag_id': dag_id,
            'run_id': run_id,
            'state': 'running',
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Create log file for this run
        logs_path = ensure_logs_dir()
        log_file = os.path.join(logs_path, f"{run_id}.log")
        try:
            with open(log_file, 'w') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting DAG run: {dag_id}\n")
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Run ID: {run_id}\n")
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Executing tasks...\n")
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Run completed successfully.\n")
        except:
            pass
        
        return redirect(url_for('view_run_log', dag_id=dag_id, run_id=run_id))
    
    return render_template_string(TRIGGER_TEMPLATE, dag=DAGS[dag_id], dag_id=dag_id, user=session.get('user'))

@app.route('/dags/<dag_id>/runs/<path:run_id>/log')
def view_run_log(dag_id, run_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if dag_id not in DAGS:
        return "DAG not found", 404
    
    # VULNERABILITY: Path traversal - run_id is used directly in file path
    # without proper sanitization
    logs_path = get_logs_base_path()
    log_file = os.path.join(logs_path, f"{run_id}.log")
    
    log_content = None
    error = None
    
    try:
        # Vulnerable file read - no path validation
        with open(log_file, 'r') as f:
            log_content = f.read()
    except FileNotFoundError:
        error = f"Log file not found for run: {run_id}"
    except Exception as e:
        error = f"Error reading log: {str(e)}"
    
    return render_template_string(LOG_VIEW_TEMPLATE, 
                                  dag_id=dag_id, 
                                  run_id=run_id, 
                                  log_content=log_content, 
                                  error=error,
                                  user=session.get('user'))

# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FlowOrchestrator - Login</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }
        .login-container { max-width: 400px; margin: 100px auto; padding: 30px; background: #16213e; border-radius: 8px; }
        h1 { color: #0f3460; text-align: center; }
        h1 { color: #e94560; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: none; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #c73e54; }
        .error { color: #ff6b6b; text-align: center; margin: 10px 0; }
        .hint { color: #888; font-size: 12px; text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🔄 FlowOrchestrator</h1>
        <p style="text-align: center; color: #888;">Workflow Management Platform</p>
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p class="hint">Demo: operator / workflow2024</p>
    </div>
</body>
</html>
'''

HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FlowOrchestrator - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { margin: 0; color: #e94560; }
        .navbar a { color: #eee; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .dag-list { display: grid; gap: 20px; }
        .dag-card { background: #16213e; padding: 20px; border-radius: 8px; border-left: 4px solid #e94560; }
        .dag-card h3 { margin-top: 0; color: #e94560; }
        .dag-card p { color: #aaa; margin: 5px 0; }
        .status { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; }
        .status.active { background: #27ae60; }
        .status.paused { background: #95a5a6; }
        .btn { display: inline-block; padding: 8px 16px; background: #e94560; color: white; text-decoration: none; border-radius: 4px; margin-top: 10px; }
        .btn:hover { background: #c73e54; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🔄 FlowOrchestrator</h1>
        <div>
            <span>Welcome, {{ user }}</span>
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <h2>Workflows (DAGs)</h2>
        <div class="dag-list">
            {% for dag_id, dag in dags.items() %}
            <div class="dag-card">
                <h3>{{ dag.name }}</h3>
                <p>{{ dag.description }}</p>
                <p><strong>Schedule:</strong> {{ dag.schedule }}</p>
                <span class="status {{ 'active' if dag.active else 'paused' }}">
                    {{ 'Active' if dag.active else 'Paused' }}
                </span>
                <br>
                <a href="/dags/{{ dag_id }}" class="btn">View Details</a>
                <a href="/dags/{{ dag_id }}/trigger" class="btn">Trigger Run</a>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

DAG_DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FlowOrchestrator - {{ dag.name }}</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { margin: 0; color: #e94560; }
        .navbar a { color: #eee; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .back-link { color: #e94560; text-decoration: none; }
        .info-box { background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #0f3460; }
        .btn { display: inline-block; padding: 8px 16px; background: #e94560; color: white; text-decoration: none; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🔄 FlowOrchestrator</h1>
        <div>
            <span>Welcome, {{ user }}</span>
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <a href="/" class="back-link">← Back to Dashboard</a>
        <h2>{{ dag.name }}</h2>
        <div class="info-box">
            <p><strong>Description:</strong> {{ dag.description }}</p>
            <p><strong>Schedule:</strong> {{ dag.schedule }}</p>
            <p><strong>Status:</strong> {{ 'Active' if dag.active else 'Paused' }}</p>
        </div>
        <a href="/dags/{{ dag_id }}/trigger" class="btn">Trigger New Run</a>
        
        <h3>Recent Runs</h3>
        {% if runs %}
        <table>
            <tr>
                <th>Run ID</th>
                <th>Start Time</th>
                <th>State</th>
                <th>Actions</th>
            </tr>
            {% for run in runs %}
            <tr>
                <td>{{ run.run_id }}</td>
                <td>{{ run.start_time }}</td>
                <td>{{ run.state }}</td>
                <td><a href="/dags/{{ dag_id }}/runs/{{ run.run_id }}/log" class="btn">View Log</a></td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>No runs yet. Trigger a new run to get started.</p>
        {% endif %}
    </div>
</body>
</html>
'''

TRIGGER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FlowOrchestrator - Trigger {{ dag.name }}</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { margin: 0; color: #e94560; }
        .navbar a { color: #eee; text-decoration: none; margin-left: 20px; }
        .container { max-width: 800px; margin: 30px auto; padding: 0 20px; }
        .back-link { color: #e94560; text-decoration: none; }
        .form-box { background: #16213e; padding: 30px; border-radius: 8px; margin: 20px 0; }
        label { display: block; margin-bottom: 8px; color: #aaa; }
        input[type="text"] { width: 100%; padding: 12px; border: none; border-radius: 4px; box-sizing: border-box; margin-bottom: 20px; }
        .btn { display: inline-block; padding: 12px 24px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #c73e54; }
        .note { color: #888; font-size: 13px; margin-top: -15px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🔄 FlowOrchestrator</h1>
        <div>
            <span>Welcome, {{ user }}</span>
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <a href="/dags/{{ dag_id }}" class="back-link">← Back to {{ dag.name }}</a>
        <h2>Trigger DAG Run</h2>
        <div class="form-box">
            <form method="POST">
                <label for="run_id">Run ID (optional)</label>
                <input type="text" name="run_id" id="run_id" placeholder="Enter custom run ID or leave blank for auto-generated">
                <p class="note">Custom run ID will be used for log file identification</p>
                <button type="submit" class="btn">Trigger Run</button>
            </form>
        </div>
    </div>
</body>
</html>
'''

LOG_VIEW_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FlowOrchestrator - Run Log</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { margin: 0; color: #e94560; }
        .navbar a { color: #eee; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .back-link { color: #e94560; text-decoration: none; }
        .log-box { background: #0d1117; padding: 20px; border-radius: 8px; margin: 20px 0; font-family: monospace; white-space: pre-wrap; overflow-x: auto; }
        .error { background: #5c1a1a; padding: 15px; border-radius: 4px; color: #ff6b6b; }
        .info { background: #16213e; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🔄 FlowOrchestrator</h1>
        <div>
            <span>Welcome, {{ user }}</span>
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <a href="/dags/{{ dag_id }}" class="back-link">← Back to DAG</a>
        <h2>Run Log</h2>
        <div class="info">
            <p><strong>DAG:</strong> {{ dag_id }}</p>
            <p><strong>Run ID:</strong> {{ run_id }}</p>
        </div>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% elif log_content %}
        <div class="log-box">{{ log_content }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    # Ensure logs directory exists with sample logs
    logs_path = ensure_logs_dir()
    
    # Create some sample log files
    sample_logs = {
        'manual__1703000000': 'ETL Pipeline run started\nProcessing data...\nCompleted successfully.',
        'scheduled__1703100000': 'Report generator started\nGenerating reports...\nCompleted.'
    }
    
    for run_id, content in sample_logs.items():
        log_file = os.path.join(logs_path, f"{run_id}.log")
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write(content)
    
    app.run(host='0.0.0.0', port=80, debug=False)
