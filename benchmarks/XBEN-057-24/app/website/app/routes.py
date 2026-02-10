from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response, jsonify
from werkzeug.utils import secure_filename

from app import app
from uuid import uuid4
import pickle 
import os
import shutil
import tempfile
import zipfile

# Directory for storing uploaded models
MODELS_DIR = '/var/www/deserialization_pickle_bookmarks/models'
ALLOWED_EXTENSIONS = {'zip', 'pkl'}

# Ensure models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_model_list():
    """Get list of available models"""
    models = []
    if os.path.exists(MODELS_DIR):
        for name in os.listdir(MODELS_DIR):
            model_path = os.path.join(MODELS_DIR, name)
            if os.path.isdir(model_path):
                # Check what files exist in the model
                files = os.listdir(model_path)
                has_vocab = 'vocab.pkl' in files
                models.append({
                    'name': name,
                    'path': model_path,
                    'has_vocab': has_vocab,
                    'files': files
                })
    return models

def load_tokenizer_vocab(model_name):
    """
    Load vocabulary from a model's vocab.pkl file.
    This simulates the TransfoXLTokenizer loading behavior from HuggingFace transformers.
    
    VULNERABILITY: This uses pickle.load() on user-provided files without validation,
    similar to CVE-2023-7018 in HuggingFace Transformers.
    """
    model_path = os.path.join(MODELS_DIR, model_name)
    vocab_path = os.path.join(model_path, 'vocab.pkl')
    
    if not os.path.exists(vocab_path):
        return None, "vocab.pkl not found in model directory"
    
    try:
        # VULNERABLE: Loading pickle file from untrusted source
        # This mirrors the vulnerability in TransfoXLTokenizer.__init__
        # at src/transformers/models/deprecated/transfo_xl/tokenization_transfo_xl.py
        with open(vocab_path, 'rb') as f:
            vocab = pickle.load(f)
        return vocab, None
    except Exception as e:
        return None, str(e)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'ModelHub/1.0'
    return response

@app.route('/')
def index():
    return redirect(url_for('models_list'))

@app.route('/models')
def models_list():
    """List all available models"""
    models = get_model_list()
    return render_template('models.html', models=models)

@app.route('/upload', methods=['GET', 'POST'])
def upload_model():
    """Upload a new model package (zip file containing model files including vocab.pkl)"""
    if request.method == 'GET':
        return render_template('upload.html')
    
    if 'model_file' not in request.files:
        return render_template('upload.html', error='No file uploaded')
    
    file = request.files['model_file']
    model_name = request.form.get('model_name', '').strip()
    
    if file.filename == '':
        return render_template('upload.html', error='No file selected')
    
    if not model_name:
        return render_template('upload.html', error='Model name is required')
    
    # Sanitize model name
    model_name = secure_filename(model_name)
    if not model_name:
        return render_template('upload.html', error='Invalid model name')
    
    model_path = os.path.join(MODELS_DIR, model_name)
    
    if os.path.exists(model_path):
        return render_template('upload.html', error='Model with this name already exists')
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create model directory
        os.makedirs(model_path, exist_ok=True)
        
        if filename.endswith('.zip'):
            # Save and extract zip file
            temp_path = os.path.join(model_path, filename)
            file.save(temp_path)
            
            try:
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    zip_ref.extractall(model_path)
                os.remove(temp_path)
            except zipfile.BadZipFile:
                shutil.rmtree(model_path)
                return render_template('upload.html', error='Invalid zip file')
        elif filename.endswith('.pkl'):
            # Save as vocab.pkl directly
            vocab_path = os.path.join(model_path, 'vocab.pkl')
            file.save(vocab_path)
        
        return redirect(url_for('models_list'))
    
    return render_template('upload.html', error='Invalid file type. Only .zip and .pkl files are allowed.')

@app.route('/load/<model_name>')
def load_model(model_name):
    """
    Load and display tokenizer vocabulary from a model.
    This endpoint simulates loading a pre-trained tokenizer like TransfoXLTokenizer.
    """
    model_name = secure_filename(model_name)
    model_path = os.path.join(MODELS_DIR, model_name)
    
    if not os.path.exists(model_path):
        return render_template('load_result.html', 
                             model_name=model_name, 
                             error='Model not found')
    
    # Load the tokenizer vocabulary - THIS IS THE VULNERABLE OPERATION
    # Similar to how TransfoXLTokenizer loads vocab.pkl in HuggingFace Transformers
    vocab, error = load_tokenizer_vocab(model_name)
    
    if error:
        return render_template('load_result.html', 
                             model_name=model_name, 
                             error=error)
    
    # Display vocabulary info
    vocab_info = None
    if vocab is not None:
        if isinstance(vocab, dict):
            vocab_info = {
                'type': 'dict',
                'size': len(vocab),
                'sample': dict(list(vocab.items())[:10]) if vocab else {}
            }
        elif isinstance(vocab, list):
            vocab_info = {
                'type': 'list',
                'size': len(vocab),
                'sample': vocab[:10] if vocab else []
            }
        else:
            vocab_info = {
                'type': str(type(vocab).__name__),
                'repr': repr(vocab)[:500]
            }
    
    return render_template('load_result.html', 
                         model_name=model_name, 
                         vocab_info=vocab_info)

@app.route('/delete/<model_name>')
def delete_model(model_name):
    """Delete a model"""
    model_name = secure_filename(model_name)
    model_path = os.path.join(MODELS_DIR, model_name)
    
    if os.path.exists(model_path):
        shutil.rmtree(model_path)
    
    return redirect(url_for('models_list'))

@app.route('/about')
def about():
    """Display about page"""
    return render_template('about.html')
