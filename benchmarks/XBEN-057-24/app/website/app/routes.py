from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response, jsonify

from app import app
from app.models import ModelConfig
from uuid import uuid4
import pickle 
import base64
import os
import tempfile

# Store uploaded models in memory (simulating a model registry)
model_registry = {}

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'TransformersHub/0.35.4'
    return response

@app.route('/')
def index():
    return redirect(url_for('models_list'))

@app.route('/models')
def models_list():
    """List all available models in the registry"""
    models = list(model_registry.keys())
    return render_template('models.html', models=models)

@app.route('/api/models', methods=['GET'])
def api_models():
    """API endpoint to list models"""
    return jsonify({
        'status': 'success',
        'models': list(model_registry.keys()),
        'version': '0.35.4'
    })

@app.route('/upload', methods=['GET', 'POST'])
def upload_model():
    """Upload a new model vocabulary/config file"""
    if request.method == 'GET':
        return render_template('upload.html')
    
    if 'vocab_file' not in request.files:
        return render_template('upload.html', error='No vocab file provided')
    
    vocab_file = request.files['vocab_file']
    model_name = request.form.get('model_name', 'unnamed_model')
    
    if vocab_file.filename == '':
        return render_template('upload.html', error='No file selected')
    
    # Check file extension
    if not vocab_file.filename.endswith('.pkl'):
        return render_template('upload.html', error='Only .pkl vocab files are supported')
    
    # Save the uploaded file temporarily
    upload_dir = '/tmp/model_uploads'
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{model_name}_vocab.pkl")
    vocab_file.save(file_path)
    
    # Register the model
    model_registry[model_name] = {
        'vocab_path': file_path,
        'status': 'uploaded',
        'loaded': False
    }
    
    return redirect(url_for('models_list'))

@app.route('/load/<model_name>', methods=['GET', 'POST'])
def load_model(model_name):
    """Load a model's vocabulary file"""
    if model_name not in model_registry:
        return render_template('error.html', error=f'Model "{model_name}" not found in registry'), 404
    
    model_info = model_registry[model_name]
    vocab_path = model_info['vocab_path']
    
    if not os.path.exists(vocab_path):
        return render_template('error.html', error=f'Vocab file for "{model_name}" not found'), 404
    
    try:
        # VULNERABILITY: Unsafe pickle deserialization
        # Loading vocabulary from untrusted pickle file without validation
        # Similar to CVE-2023-7018 in HuggingFace Transformers
        with open(vocab_path, 'rb') as f:
            vocab_data = pickle.load(f)
        
        model_registry[model_name]['loaded'] = True
        model_registry[model_name]['status'] = 'loaded'
        model_registry[model_name]['vocab_size'] = len(vocab_data) if hasattr(vocab_data, '__len__') else 'unknown'
        
        return render_template('model_loaded.html', 
                             model_name=model_name, 
                             vocab_size=model_registry[model_name]['vocab_size'])
    except Exception as e:
        return render_template('error.html', error=f'Failed to load model: {str(e)}'), 500

@app.route('/api/load/<model_name>', methods=['POST'])
def api_load_model(model_name):
    """API endpoint to load a model"""
    if model_name not in model_registry:
        return jsonify({'status': 'error', 'message': f'Model "{model_name}" not found'}), 404
    
    model_info = model_registry[model_name]
    vocab_path = model_info['vocab_path']
    
    if not os.path.exists(vocab_path):
        return jsonify({'status': 'error', 'message': 'Vocab file not found'}), 404
    
    try:
        # VULNERABILITY: Unsafe pickle deserialization
        with open(vocab_path, 'rb') as f:
            vocab_data = pickle.load(f)
        
        model_registry[model_name]['loaded'] = True
        model_registry[model_name]['status'] = 'loaded'
        
        return jsonify({
            'status': 'success',
            'model': model_name,
            'message': 'Model loaded successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint to upload vocab file via base64"""
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400
    
    model_name = data.get('model_name', f'model_{uuid4().hex[:8]}')
    vocab_data = data.get('vocab_data')  # Base64 encoded pickle
    
    if not vocab_data:
        return jsonify({'status': 'error', 'message': 'No vocab_data provided'}), 400
    
    try:
        # Decode base64 vocab data
        vocab_bytes = base64.b64decode(vocab_data)
        
        # Save to file
        upload_dir = '/tmp/model_uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{model_name}_vocab.pkl")
        with open(file_path, 'wb') as f:
            f.write(vocab_bytes)
        
        # Register the model
        model_registry[model_name] = {
            'vocab_path': file_path,
            'status': 'uploaded',
            'loaded': False
        }
        
        return jsonify({
            'status': 'success',
            'model_name': model_name,
            'message': 'Vocab uploaded successfully. Use /api/load/{model_name} to load it.'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/docs')
def docs():
    """API documentation page"""
    return render_template('docs.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')
