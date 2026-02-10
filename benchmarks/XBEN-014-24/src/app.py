import os
import json
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response

app = Flask(__name__)
app.config["SECRET_KEY"] = "Dtale"

FLAG = os.environ.get('FLAG', 'FLAG{test_flag}')

users_db = {
    "admin": {
        "password": "X9k#mP2$vL7@nQ4w",
        "role": "admin"
    },
    "analyst": {
        "password": "analyst123",
        "role": "user"
    }
}

datasets = {}

def init_datasets():
    global datasets
    datasets["1"] = {
        "name": "Sales Report Q4",
        "owner": "analyst",
        "data": pd.DataFrame({
            "product": ["Widget A", "Widget B", "Widget C", "Widget D"],
            "revenue": [15000, 22000, 18500, 31000],
            "units": [150, 220, 185, 310],
            "region": ["North", "South", "East", "West"]
        }),
        "settings": {
            "enable_custom_filters": False,
            "query": None
        }
    }
    datasets["2"] = {
        "name": "System Metrics",
        "owner": "admin",
        "data": pd.DataFrame({
            "metric_name": ["cpu_usage", "memory_usage", "disk_io", "network_latency", "secret_key"],
            "current_value": [45.2, 78.1, 120.5, 12.3, 0.0],
            "threshold": [80.0, 90.0, 200.0, 50.0, 0.0],
            "status": ["OK", "WARNING", "OK", "OK", "FLAG: " + FLAG]
        }),
        "settings": {
            "enable_custom_filters": False,
            "query": None
        }
    }

init_datasets()

def check_auth():
    return session.get('logged_in', False)

def get_current_user():
    return session.get('username', None)

def is_admin():
    username = get_current_user()
    if username and username in users_db:
        return users_db[username].get('role') == 'admin'
    return False

@app.route('/')
def index():
    if check_auth():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in users_db and users_db[username]['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not check_auth():
        return redirect(url_for('login'))
    
    user = get_current_user()
    admin = is_admin()
    
    visible_datasets = []
    for data_id, dataset in datasets.items():
        if admin or dataset['owner'] == user:
            visible_datasets.append({
                'id': data_id,
                'name': dataset['name'],
                'owner': dataset['owner']
            })
    
    return render_template('dashboard.html', 
                         username=user, 
                         is_admin=admin,
                         datasets=visible_datasets)

@app.route('/data/<data_id>')
def view_data(data_id):
    if not check_auth():
        return redirect(url_for('login'))
    
    if data_id not in datasets:
        return "Dataset not found", 404
    
    dataset = datasets[data_id]
    user = get_current_user()
    admin = is_admin()
    
    if not admin and dataset['owner'] != user:
        return "Access denied", 403
    
    df = dataset['data'].copy()
    
    query = dataset['settings'].get('query')
    if query:
        try:
            df = df.query(query)
        except Exception:
            pass
    
    return render_template('data_view.html',
                         dataset_name=dataset['name'],
                         data_id=data_id,
                         columns=list(df.columns),
                         rows=df.values.tolist(),
                         settings=dataset['settings'])

@app.route('/update-settings/<data_id>', methods=['GET', 'POST'])
def update_settings(data_id):
    if not check_auth():
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    if data_id not in datasets:
        return jsonify({"success": False, "error": "Dataset not found"}), 404
    
    dataset = datasets[data_id]
    user = get_current_user()
    admin = is_admin()
    
    if not admin and dataset['owner'] != user:
        return jsonify({"success": False, "error": "Access denied"}), 403
    
    settings_param = request.args.get('settings') or request.form.get('settings')
    if not settings_param:
        try:
            settings_param = request.get_json()
            if settings_param:
                settings_param = json.dumps(settings_param.get('settings', {}))
        except:
            pass
    
    if settings_param:
        try:
            updated_settings = json.loads(settings_param) if isinstance(settings_param, str) else settings_param
        except json.JSONDecodeError:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400
        
        if not dataset['settings'].get('enable_custom_filters', False):
            updated_settings.pop('query', None)
        
        dataset['settings'].update(updated_settings)
    
    return jsonify({"success": True})

@app.route('/api/query/<data_id>', methods=['POST'])
def execute_query(data_id):
    if not check_auth():
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    if data_id not in datasets:
        return jsonify({"success": False, "error": "Dataset not found"}), 404
    
    dataset = datasets[data_id]
    user = get_current_user()
    admin = is_admin()
    
    if not admin and dataset['owner'] != user:
        return jsonify({"success": False, "error": "Access denied"}), 403
    
    if not dataset['settings'].get('enable_custom_filters', False):
        return jsonify({"success": False, "error": "Custom filters are disabled"}), 403
    
    query = request.json.get('query', '')
    if not query:
        return jsonify({"success": False, "error": "No query provided"}), 400
    
    df = dataset['data'].copy()
    try:
        result = df.query(query)
        return jsonify({
            "success": True,
            "columns": list(result.columns),
            "data": result.values.tolist()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
