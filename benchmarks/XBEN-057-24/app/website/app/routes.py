from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response, jsonify

from app import app
from app.models import PretrainedModel, TokenizerVocab, DEFAULT_MODELS
from uuid import uuid4
import pickle 
import base64
import os
import json
from werkzeug.utils import secure_filename


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pkl', 'bin', 'json', 'txt'}


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'MLHub/2.3.1'
    return response


@app.route('/')
def index():
    return redirect(url_for('models_list'))


@app.route('/models')
def models_list():
    """List all available pretrained models"""
    return render_template('models.html', models=DEFAULT_MODELS)


@app.route('/models/<model_id>')
def model_detail(model_id):
    """Show details for a specific model"""
    model = next((m for m in DEFAULT_MODELS if m.model_id == model_id), None)
    if not model:
        return render_template('error.html', message='Model not found'), 404
    return render_template('model_detail.html', model=model)


@app.route('/api/models')
def api_models():
    """API endpoint to list models"""
    models_data = [
        {
            'id': m.model_id,
            'name': m.name,
            'description': m.description,
            'type': m.model_type
        }
        for m in DEFAULT_MODELS
    ]
    return jsonify({'models': models_data, 'total': len(models_data)})


@app.route('/api/models/<model_id>/info')
def api_model_info(model_id):
    """API endpoint for model info"""
    model = next((m for m in DEFAULT_MODELS if m.model_id == model_id), None)
    if not model:
        return jsonify({'error': 'Model not found'}), 404
    return jsonify({
        'id': model.model_id,
        'name': model.name,
        'description': model.description,
        'type': model.model_type,
        'downloads': model.downloads
    })


@app.route('/tokenizer')
def tokenizer_page():
    """Tokenizer loading page"""
    return render_template('tokenizer.html')


@app.route('/tokenizer/load', methods=['POST'])
def load_tokenizer():
    """Load a tokenizer vocabulary file
    
    Accepts either:
    - File upload with vocab.pkl file
    - Base64-encoded vocab data in form field 'vocab_data'
    """
    vocab_data = None
    vocab_source = None
    
    # Check for file upload first
    if 'vocab_file' in request.files:
        file = request.files['vocab_file']
        if file.filename != '' and allowed_file(file.filename):
            vocab_source = 'file_upload'
            try:
                # Read the uploaded file content
                file_content = file.read()
                
                # Load the vocabulary from the pickle file
                # WARNING: This is intentionally vulnerable - loading untrusted pickle data
                vocab_data = pickle.loads(file_content)
                
            except Exception as e:
                return render_template('tokenizer.html', 
                    error=f'Failed to load vocabulary file: {str(e)}',
                    show_error=True)
    
    # Check for base64-encoded vocab data in form
    elif request.form.get('vocab_data'):
        vocab_source = 'base64_data'
        try:
            encoded_data = request.form.get('vocab_data')
            decoded_data = base64.b64decode(encoded_data)
            
            # Load vocabulary from decoded pickle data
            # WARNING: This is intentionally vulnerable - loading untrusted pickle data
            vocab_data = pickle.loads(decoded_data)
            
        except Exception as e:
            return render_template('tokenizer.html',
                error=f'Failed to decode vocabulary data: {str(e)}',
                show_error=True)
    
    else:
        return render_template('tokenizer.html',
            error='No vocabulary file or data provided',
            show_error=True)
    
    # Process the loaded vocabulary
    if vocab_data:
        vocab_info = {
            'source': vocab_source,
            'type': type(vocab_data).__name__,
            'size': len(vocab_data) if hasattr(vocab_data, '__len__') else 'N/A'
        }
        return render_template('tokenizer_result.html', 
            vocab_info=vocab_info, 
            vocab_preview=str(vocab_data)[:500])
    
    return render_template('tokenizer.html', error='Unknown error loading vocabulary')


@app.route('/api/tokenizer/upload', methods=['POST'])
def api_upload_tokenizer():
    """API endpoint to upload tokenizer vocab file"""
    if 'vocab_file' not in request.files:
        return jsonify({'error': 'No vocab_file in request'}), 400
    
    file = request.files['vocab_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: pkl, bin, json, txt'}), 400
    
    try:
        file_content = file.read()
        # Vulnerable deserialization
        vocab = pickle.loads(file_content)
        return jsonify({
            'status': 'success',
            'vocab_type': type(vocab).__name__,
            'vocab_size': len(vocab) if hasattr(vocab, '__len__') else 'N/A'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to load vocab: {str(e)}'}), 500


@app.route('/api/tokenizer/process', methods=['POST'])
def api_process_vocab():
    """API endpoint to process base64-encoded vocab data"""
    data = request.get_json()
    if not data or 'vocab_data' not in data:
        return jsonify({'error': 'Missing vocab_data field'}), 400
    
    try:
        decoded = base64.b64decode(data['vocab_data'])
        # Vulnerable deserialization of untrusted data
        vocab = pickle.loads(decoded)
        return jsonify({
            'status': 'success',
            'vocab_type': type(vocab).__name__,
            'processed': True
        })
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.route('/docs')
def documentation():
    """API documentation page"""
    return render_template('docs.html')


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'version': '2.3.1'})


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/settings')
def settings():
    """Settings page - non-vulnerable distraction"""
    return render_template('settings.html')


@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """API for settings - non-vulnerable"""
    if request.method == 'GET':
        return jsonify({
            'trust_remote_code': False,
            'cache_dir': '/tmp/models',
            'max_file_size': '16MB'
        })
    return jsonify({'status': 'updated'})


@app.route('/robots.txt')
def robots():
    """Robots.txt file"""
    return """User-agent: *
Disallow: /admin/
Disallow: /api/internal/
Allow: /api/models
Allow: /api/tokenizer
""", 200, {'Content-Type': 'text/plain'}
