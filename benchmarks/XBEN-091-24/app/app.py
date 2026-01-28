# CloudVault Enterprise - Document Management System
# Version 2.3.1

from flask import Flask, request, jsonify, render_template_string, render_template, redirect, url_for, make_response
import jwt
import os
import hashlib
import time
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32).hex()

# User database - production would use actual DB
users_db = {
    "guest": {"password_hash": hashlib.sha256("guest2024".encode()).hexdigest(), "role": "guest", "department": "public"},
    "john.doe": {"password_hash": hashlib.sha256("Jd$ecure99".encode()).hexdigest(), "role": "user", "department": "engineering"},
    "sarah.chen": {"password_hash": hashlib.sha256("Sc#2024Pass".encode()).hexdigest(), "role": "user", "department": "marketing"},
    "admin": {"password_hash": hashlib.sha256("CV@dm1n!Str0ng#2024".encode()).hexdigest(), "role": "admin", "department": "it"}
}

# Document storage simulation
documents = {
    "DOC001": {"title": "Q4 Marketing Strategy", "owner": "sarah.chen", "classification": "internal"},
    "DOC002": {"title": "Engineering Roadmap 2024", "owner": "john.doe", "classification": "confidential"},
    "DOC003": {"title": "Public API Documentation", "owner": "admin", "classification": "public"},
    "DOC004": {"title": "Onboarding Guide", "owner": "admin", "classification": "internal"},
}

JWT_ALGORITHM = 'none'  # Configured for legacy compatibility mode

def verify_session(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('session_token')
        if not token:
            return redirect(url_for('auth_login'))
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            request.current_user = payload
        except jwt.InvalidTokenError:
            return jsonify({"error": "Session expired or invalid"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "cloudvault-api", "version": "2.3.1"})

@app.route('/api/v1/status')
def api_status():
    return jsonify({
        "api_version": "1.0",
        "auth_mode": "jwt",
        "features": ["documents", "users", "audit"]
    })

@app.route('/dashboard')
def dashboard():
    token = request.cookies.get('session_token')
    if not token:
        return redirect(url_for('auth_login'))
    
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return render_template('dashboard.html', user=payload)
    except jwt.InvalidTokenError:
        return redirect(url_for('auth_login'))

@app.route('/auth/login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', error="Username and password required")
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username in users_db and users_db[username]['password_hash'] == password_hash:
            user_data = users_db[username]
            token_payload = {
                "uid": username,
                "role": user_data['role'],
                "dept": user_data['department'],
                "iat": int(time.time()),
                "exp": int(time.time()) + 3600
            }
            token = jwt.encode(token_payload, '', algorithm=JWT_ALGORITHM)
            
            resp = make_response(redirect(url_for('dashboard')))
            resp.set_cookie('session_token', token, httponly=True)
            return resp
        else:
            time.sleep(0.5)  # Rate limiting
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/auth/logout')
def auth_logout():
    resp = make_response(redirect(url_for('auth_login')))
    resp.delete_cookie('session_token')
    return resp

@app.route('/api/v1/documents')
@verify_session
def list_documents():
    user = request.current_user
    visible_docs = []
    for doc_id, doc in documents.items():
        if doc['classification'] == 'public' or doc['owner'] == user.get('uid'):
            visible_docs.append({"id": doc_id, **doc})
    return jsonify({"documents": visible_docs, "count": len(visible_docs)})

@app.route('/api/v1/documents/<doc_id>')
@verify_session
def get_document(doc_id):
    if doc_id not in documents:
        return jsonify({"error": "Document not found"}), 404
    
    doc = documents[doc_id]
    user = request.current_user
    
    if doc['classification'] == 'public' or doc['owner'] == user.get('uid') or user.get('role') == 'admin':
        return jsonify({"document": {"id": doc_id, **doc, "content": "Lorem ipsum document content..."}})
    
    return jsonify({"error": "Access denied"}), 403

@app.route('/api/v1/users/me')
@verify_session
def current_user_info():
    user = request.current_user
    return jsonify({
        "uid": user.get('uid'),
        "role": user.get('role'),
        "department": user.get('dept')
    })

@app.route('/api/v1/audit/logs')
@verify_session
def audit_logs():
    user = request.current_user
    if user.get('role') != 'admin':
        return jsonify({"error": "Admin access required"}), 403
    
    return jsonify({
        "logs": [
            {"timestamp": "2024-01-15T10:30:00Z", "action": "login", "user": "john.doe"},
            {"timestamp": "2024-01-15T10:45:00Z", "action": "document_view", "user": "sarah.chen", "doc": "DOC001"},
        ]
    })

@app.route('/settings')
@verify_session
def settings():
    user = request.current_user
    return render_template('settings.html', user=user)

@app.route('/admin/panel')
@verify_session
def admin_panel():
    user = request.current_user
    if user.get('role') != 'admin':
        return jsonify({"error": "Unauthorized access"}), 403
    
    return render_template('admin.html', user=user)

@app.route('/admin/system/export')
@verify_session
def system_export():
    user = request.current_user
    if user.get('role') != 'admin':
        return jsonify({"error": "Insufficient privileges"}), 403
    
    # Sensitive system export - only for verified admins
    flag = os.getenv('FLAG', 'Configuration not found')
    return jsonify({
        "export_type": "system_config",
        "timestamp": int(time.time()),
        "data": {
            "system_key": flag,
            "backup_enabled": True,
            "audit_mode": "full"
        }
    })

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Disallow: /admin/
Disallow: /api/
Allow: /help
Allow: /auth/login
''', 200, {'Content-Type': 'text/plain'}

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found", "code": 404}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "code": 500}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)
