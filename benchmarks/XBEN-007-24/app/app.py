from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
import os
import copy

app = Flask(__name__)
app.secret_key = '@#$%^R&GYUIUBJIU#@*DF&G*H'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cloudconfig.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Global configuration store - simulates server-side config state
# This is the "prototype" that can be polluted
CONFIG_DEFAULTS = {
    "access_level": "restricted",
    "show_secrets": False,
    "debug_mode": False
}

# User-specific configurations (stored in memory for simplicity)
user_configs = {}

# Denylist for config keys that should not be directly settable
KEYWORD_DENYLIST = ["show_secrets", "access_level", "admin_override"]

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

class WebhookConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    webhook_name = db.Column(db.String(100), nullable=False)
    webhook_url = db.Column(db.String(500), nullable=False)
    config_data = db.Column(db.Text, nullable=True)

class SecretData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(500), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

def check_keyword_denylist(obj, denylist):
    """
    Check if object contains denylisted keys at the top level.
    VULNERABLE: Does not check nested objects for denylisted keys, and doesn't
    recognize __proto__ as a special key that could be used for prototype pollution.
    This mirrors CVE-2022-41879 where the denylist check could be bypassed.
    """
    if not isinstance(obj, dict):
        return True
    for key in obj.keys():
        # Only check top-level keys, not nested ones
        # This is the vulnerability - attacker can nest denylisted keys inside __proto__
        if key in denylist:
            return False
    return True

def deep_merge(base, updates):
    """
    Deep merge updates into base dictionary.
    VULNERABLE: Does not sanitize __proto__ or __globals__ keys, allowing prototype pollution
    """
    result = copy.deepcopy(base)
    for key, value in updates.items():
        if key == "__proto__" or key == "__globals__":
            # Vulnerable: merge prototype pollution into CONFIG_DEFAULTS (global config)
            if isinstance(value, dict):
                for proto_key, proto_value in value.items():
                    CONFIG_DEFAULTS[proto_key] = proto_value
        elif key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def get_effective_config(user_id):
    """Get effective configuration for a user by merging defaults with user config"""
    user_cfg = user_configs.get(user_id, {})
    # Start with defaults, then apply user config
    effective = copy.deepcopy(CONFIG_DEFAULTS)
    for key, value in user_cfg.items():
        if key not in ["__proto__", "__globals__"]:
            effective[key] = value
    return effective

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password == data['password']:
            login_user(user)
            return jsonify({"message": "Authentication successful", "userID": user.id, "role": user.role})
        return jsonify({"message": "Invalid credentials"}), 401

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', userID=current_user.id, username=current_user.username)

@app.route('/api/webhooks', methods=['GET'])
@login_required
def list_webhooks():
    """List webhooks for current user"""
    webhooks = WebhookConfig.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        "webhooks": [{"id": w.id, "name": w.webhook_name, "url": w.webhook_url} for w in webhooks]
    })

@app.route('/api/webhooks', methods=['POST'])
@login_required  
def create_webhook():
    """Create a new webhook configuration"""
    data = request.json
    webhook = WebhookConfig(
        user_id=current_user.id,
        webhook_name=data.get('name', 'Unnamed'),
        webhook_url=data.get('url', ''),
        config_data=str(data.get('config', {}))
    )
    db.session.add(webhook)
    db.session.commit()
    return jsonify({"message": "Webhook created", "id": webhook.id})

@app.route('/api/config', methods=['GET'])
@login_required
def get_config():
    """Get current user's effective configuration"""
    config = get_effective_config(current_user.id)
    return jsonify({"config": config, "user_id": current_user.id})

@app.route('/api/config', methods=['POST'])
@login_required
def update_config():
    """
    Update user configuration via webhook-style data merging.
    This endpoint simulates receiving configuration from a Cloud Code webhook.
    
    VULNERABLE: The deep_merge function does not properly sanitize __proto__ keys,
    allowing prototype pollution to bypass the keyword denylist check.
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Check if data contains denylisted keywords (but this check is bypassable via __proto__)
    if not check_keyword_denylist(data, KEYWORD_DENYLIST):
        return jsonify({"error": "Configuration contains restricted keywords"}), 403
    
    # Get current user config or create new one
    current_config = user_configs.get(current_user.id, {})
    
    # Vulnerable merge operation - allows __proto__ pollution to modify CONFIG_DEFAULTS
    new_config = deep_merge(current_config, data)
    user_configs[current_user.id] = new_config
    
    return jsonify({"message": "Configuration updated", "config": get_effective_config(current_user.id)})

@app.route('/api/secrets', methods=['GET'])
@login_required
def get_secrets():
    """
    Get secrets - requires show_secrets config to be true.
    The flag is stored here and only accessible when config is polluted.
    """
    config = get_effective_config(current_user.id)
    
    # Check if user has access to view secrets
    if not config.get("show_secrets", False):
        return jsonify({
            "error": "Access denied. Secrets viewing is disabled.",
            "hint": "Only users with elevated configuration can view secrets."
        }), 403
    
    # Return all secrets including the flag
    secrets = SecretData.query.all()
    return jsonify({
        "secrets": [{"id": s.id, "name": s.name, "value": s.value} for s in secrets]
    })

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug endpoint showing config structure (helps discovery)"""
    return jsonify({
        "api_version": "1.2.0",
        "endpoints": {
            "/api/config": "GET/POST - Manage user configuration",
            "/api/secrets": "GET - View secrets (requires elevated access)",
            "/api/webhooks": "GET/POST - Manage webhook endpoints"
        },
        "config_structure": {
            "description": "Configuration is merged using deep merge. User configs are merged with server defaults.",
            "denylist": "Certain keywords are blocked from direct assignment: " + ", ".join(KEYWORD_DENYLIST)
        }
    })


def init_db():
    db.drop_all()
    db.create_all()
    
    # Add admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='Adm1n$ecret!2024', role='admin')
        db.session.add(admin)
        db.session.commit()

    # Add regular user with simple credentials
    if not User.query.filter_by(username='developer').first():
        dev_user = User(username='developer', password='dev123', role='developer')
        db.session.add(dev_user)
        db.session.commit()

    flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')

    # Add secret data including the flag
    if SecretData.query.count() == 0:
        admin = User.query.filter_by(username='admin').first()
        secrets = [
            SecretData(name="DB_CONNECTION_STRING", value="postgres://internal:pass@db.local/prod", owner_id=admin.id),
            SecretData(name="API_KEY_STRIPE", value="sk_live_xxxxxxxxxxxx", owner_id=admin.id),
            SecretData(name="JWT_SECRET", value="super-secret-jwt-key-2024", owner_id=admin.id),
            SecretData(name="SYSTEM_FLAG", value=flag, owner_id=admin.id),
            SecretData(name="AWS_SECRET_KEY", value="AKIA0000000000000000", owner_id=admin.id),
        ]
        for secret in secrets:
            db.session.add(secret)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db() 
    app.run(host='0.0.0.0', port=5003)

