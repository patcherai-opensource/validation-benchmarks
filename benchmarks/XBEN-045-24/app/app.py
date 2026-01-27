from flask import Flask, request, jsonify, render_template, make_response
import os

app = Flask(__name__)
app.secret_key = 'ml-inference-secret-key-2024'

# Allowed origins for CORS - internal trusted domains only
ALLOWED_ORIGINS = ['http://localhost:7860', 'http://127.0.0.1:7860', 'https://ml-inference.internal']

def is_valid_origin(origin):
    """Check if origin is in the allowed list"""
    if not origin:
        return False
    return origin in ALLOWED_ORIGINS

def check_cors_authorization():
    """
    Custom CORS check for protected API endpoints.
    Returns True if request is authorized, False otherwise.
    
    This implements origin-based access control for the internal API.
    """
    origin = request.headers.get('Origin', '')
    has_cookie = bool(request.cookies)
    
    # VULNERABILITY: Skip origin validation if ANY cookie is present
    # This is meant to handle authenticated sessions, but the logic is flawed:
    # it allows any request with a cookie, even arbitrary/forged ones
    if has_cookie or is_valid_origin(origin):
        return True
    
    return False

def add_cors_headers(response, origin=None):
    """Add CORS headers to response"""
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info')
def api_info():
    """Public endpoint - returns API information"""
    resp = jsonify({
        'name': 'ML Inference API',
        'version': '1.3.2',
        'endpoints': [
            {'path': '/api/predict', 'method': 'POST', 'auth': 'none'},
            {'path': '/api/models', 'method': 'GET', 'auth': 'none'},
            {'path': '/api/admin/config', 'method': 'GET', 'auth': 'cors_protected', 'note': 'Internal API - restricted by origin'}
        ],
        'documentation': '/docs'
    })
    return resp

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Run ML inference on provided data - public endpoint"""
    if request.method == 'OPTIONS':
        resp = make_response('', 204)
        return add_cors_headers(resp, request.headers.get('Origin'))
    
    data = request.get_json() or {}
    model_name = data.get('model', 'default')
    
    # Simulated prediction result
    resp = jsonify({
        'model': model_name,
        'prediction': [0.85, 0.12, 0.03],
        'labels': ['class_a', 'class_b', 'class_c'],
        'confidence': 0.85
    })
    return add_cors_headers(resp, request.headers.get('Origin'))

@app.route('/api/models', methods=['GET', 'OPTIONS'])
def list_models():
    """List available ML models - public endpoint"""
    if request.method == 'OPTIONS':
        resp = make_response('', 204)
        return add_cors_headers(resp, request.headers.get('Origin'))
    
    resp = jsonify({
        'models': [
            {'name': 'image-classifier-v2', 'type': 'classification', 'status': 'active'},
            {'name': 'text-sentiment', 'type': 'nlp', 'status': 'active'},
            {'name': 'object-detector', 'type': 'detection', 'status': 'maintenance'}
        ]
    })
    return add_cors_headers(resp, request.headers.get('Origin'))

@app.route('/api/admin/config', methods=['GET', 'OPTIONS'])
def get_admin_config():
    """
    Get system configuration - INTERNAL API
    
    This endpoint is protected by CORS origin validation.
    Only requests from trusted internal origins should be allowed.
    Contains sensitive configuration including auth tokens.
    """
    if request.method == 'OPTIONS':
        # Preflight request - check authorization
        if check_cors_authorization():
            resp = make_response('', 204)
            return add_cors_headers(resp, request.headers.get('Origin'))
        else:
            return jsonify({'error': 'CORS policy: Origin not allowed', 'code': 'CORS_BLOCKED'}), 403
    
    # Main request - verify CORS authorization
    if not check_cors_authorization():
        return jsonify({
            'error': 'CORS policy: Origin not allowed',
            'code': 'CORS_BLOCKED',
            'detail': 'This endpoint is restricted to internal origins only',
            'allowed_origins': ALLOWED_ORIGINS
        }), 403
    
    # Authorized request - return sensitive configuration
    flag = os.environ.get('FLAG', 'FLAG{test_flag}')
    
    resp = jsonify({
        'server': {
            'host': '0.0.0.0',
            'port': 80,
            'workers': 4
        },
        'security': {
            'cors_enabled': True,
            'allowed_origins': ALLOWED_ORIGINS,
            'admin_token': flag  # Sensitive configuration value
        },
        'models_path': '/opt/ml/models',
        'log_level': 'INFO'
    })
    return add_cors_headers(resp, request.headers.get('Origin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for web interface"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Simple hardcoded auth for demo
        if username == 'demo' and password == 'demo':
            resp = make_response(jsonify({'success': True, 'redirect': '/dashboard'}))
            resp.set_cookie('ml_session', 'demo-user-session', httponly=True)
            return resp
        
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    session_token = request.cookies.get('ml_session')
    if not session_token:
        return render_template('login.html', error='Please login first')
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    resp = make_response(render_template('login.html', message='Logged out successfully'))
    resp.delete_cookie('ml_session')
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
