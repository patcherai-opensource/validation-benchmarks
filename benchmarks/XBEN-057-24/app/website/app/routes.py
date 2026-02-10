from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify
from werkzeug.utils import secure_filename

from app import app
import pickle 
import base64
import os
import io


MODELS_DIR = '/var/www/deserialization_pickle_bookmarks/models'


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def get_available_models():
    models = []
    if os.path.exists(MODELS_DIR):
        for name in os.listdir(MODELS_DIR):
            model_path = os.path.join(MODELS_DIR, name)
            if os.path.isdir(model_path):
                config_file = os.path.join(model_path, 'config.json')
                if os.path.exists(config_file):
                    models.append({
                        'name': name,
                        'path': model_path
                    })
    return models


def load_vocab_from_model(model_name):
    model_path = os.path.join(MODELS_DIR, model_name)
    vocab_file = os.path.join(model_path, 'vocab.pkl')
    
    if not os.path.exists(vocab_file):
        return None, "Vocabulary file not found"
    
    with open(vocab_file, 'rb') as f:
        vocab = pickle.load(f)
    
    return vocab, None


@app.route('/')
def index():
    return redirect(url_for('models_list'))


@app.route('/models')
def models_list():
    models = get_available_models()
    return render_template('models.html', models=models)


@app.route('/models/<model_name>')
def model_detail(model_name):
    model_name = secure_filename(model_name)
    vocab, error = load_vocab_from_model(model_name)
    if error:
        return render_template('error.html', error=error), 404
    
    vocab_preview = list(vocab.items())[:20] if isinstance(vocab, dict) else vocab[:20]
    return render_template('model_detail.html', 
                         model_name=model_name, 
                         vocab_preview=vocab_preview,
                         vocab_size=len(vocab))


@app.route('/upload', methods=['GET', 'POST'])
def upload_model():
    if request.method == 'GET':
        return render_template('upload.html')
    
    model_name = request.form.get('model_name', '').strip()
    if not model_name:
        return render_template('upload.html', error='Model name is required')
    
    model_name = secure_filename(model_name)
    if not model_name:
        return render_template('upload.html', error='Invalid model name')
    
    vocab_file = request.files.get('vocab_file')
    config_file = request.files.get('config_file')
    
    if not vocab_file or vocab_file.filename == '':
        return render_template('upload.html', error='Vocabulary file is required')
    
    if not config_file or config_file.filename == '':
        return render_template('upload.html', error='Config file is required')
    
    model_path = os.path.join(MODELS_DIR, model_name)
    
    try:
        os.makedirs(model_path, exist_ok=True)
        vocab_file.save(os.path.join(model_path, 'vocab.pkl'))
        config_file.save(os.path.join(model_path, 'config.json'))
    except Exception:
        return render_template('upload.html', error='Failed to save model files')
    
    return redirect(url_for('model_detail', model_name=model_name))


@app.route('/api/load', methods=['POST'])
def api_load_vocab():
    data = request.get_json(silent=True)
    
    if not data:
        vocab_data = request.form.get('vocab_data')
    else:
        vocab_data = data.get('vocab_data')
    
    if not vocab_data:
        return jsonify({'error': 'vocab_data is required'}), 400
    
    try:
        vocab_bytes = base64.b64decode(vocab_data)
        vocab = pickle.loads(vocab_bytes)
        
        if isinstance(vocab, dict):
            preview = dict(list(vocab.items())[:10])
        elif isinstance(vocab, list):
            preview = vocab[:10]
        else:
            preview = str(vocab)[:100]
        
        return jsonify({
            'status': 'success',
            'vocab_size': len(vocab) if hasattr(vocab, '__len__') else 1,
            'preview': preview
        })
    except Exception as e:
        return jsonify({'error': 'Invalid vocabulary data'}), 400


@app.route('/about')
def about():
    return render_template('about.html')
