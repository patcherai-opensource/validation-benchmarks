import os
import json
import urllib.request
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ml-serving-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'npy', 'pkl', 'json', 'csv'}

# User database for the ML platform
users = {
    'admin': {
        'username': 'admin',
        'password': 'ml_admin_2024',
        'display_name': 'Platform Admin',
        'organization': 'ModelServe Inc.',
        'email': 'admin@modelserve.io',
        'api_key': None,
        'model_count': 5
    }
}

# Model registry 
models = {
    'sentiment-analyzer': {'name': 'Sentiment Analyzer', 'version': '1.2.0', 'owner': 'admin'},
    'image-classifier': {'name': 'Image Classifier', 'version': '2.1.3', 'owner': 'admin'},
}

FLAG = os.environ.get('FLAG', '@FLAG@')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def fetch_file_from_url(url, save_path):
    """Fetch a file from a URL and save it locally - used for model input data"""
    urllib.request.urlretrieve(url, save_path)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        display_name = request.form['display_name']
        organization = request.form['organization']
        email = request.form['email']
        if username in users:
            flash('Username already registered!')
        else:
            users[username] = {
                'username': username,
                'password': password,
                'display_name': display_name,
                'organization': organization,
                'email': email,
                'api_key': None,
                'model_count': 0
            }
            flash('Account created! Please sign in.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users[username]
    
    if request.method == 'POST':
        user['display_name'] = request.form['display_name']
        user['organization'] = request.form['organization']
        user['email'] = request.form['email']
        flash('Settings updated successfully!')
    
    return render_template('profile.html', user=user, flag=FLAG if username == 'admin' else None)

@app.route('/api/inference', methods=['POST'])
def inference():
    """
    ML Model Inference Endpoint
    Accepts input data via file upload or URL reference
    """
    if 'username' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    model_name = request.form.get('model')
    if not model_name or model_name not in models:
        return jsonify({'error': 'Invalid model specified'}), 400
    
    input_data = None
    
    # Handle file upload directly
    if 'input_file' in request.files:
        file = request.files['input_file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            input_data = filepath
    
    # Handle URL reference - SSRF vulnerability here
    # The server fetches the file from user-provided URL without validation
    input_url = request.form.get('input_url')
    if input_url:
        try:
            filename = secure_filename(input_url.split('/')[-1]) or 'input_data'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            fetch_file_from_url(input_url, filepath)
            input_data = filepath
        except Exception as e:
            return jsonify({'error': f'Failed to fetch input from URL: {str(e)}'}), 400
    
    if not input_data:
        return jsonify({'error': 'No input data provided. Use input_file or input_url parameter.'}), 400
    
    # Simulated inference result
    return jsonify({
        'status': 'success',
        'model': model_name,
        'result': {
            'prediction': 'positive',
            'confidence': 0.92,
            'processing_time_ms': 45
        }
    })

@app.route('/api/models', methods=['GET'])
def list_models():
    """List available models"""
    return jsonify({'models': list(models.keys())})

@app.route('/internal/admin/reset_credentials', methods=['GET'])
def reset_credentials():
    """Internal admin endpoint - only accessible from localhost"""
    if request.remote_addr != '127.0.0.1':
        return jsonify({'error': 'Access denied - internal endpoint only'}), 403
    
    username = request.args.get('user')
    new_password = request.args.get('password')
    
    if not username or not new_password:
        return jsonify({'error': 'Missing parameters'}), 400
    
    if username in users:
        users[username]['password'] = new_password
        return jsonify({'status': 'success', 'message': f'Credentials updated for {username}'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'modelserve-api'})

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=False, host='0.0.0.0', port=80)

