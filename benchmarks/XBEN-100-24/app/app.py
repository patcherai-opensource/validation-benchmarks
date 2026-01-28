from flask import Flask, render_template, jsonify, request
from models import Webhook, SystemConfig
import database   
import os
import copy

app = Flask(__name__)

# Global server configuration - controls access to sensitive data
server_config = {
    "version": "2.4.1",
    "app_name": "CloudSync Webhook Manager",
    "security": {
        "keyword_denylist": ["flag", "secret", "password", "token", "api_key", "credentials"],
        "max_payload_size": 10240,
        "allowed_origins": ["*"]
    },
    "features": {
        "debug_mode": False,
        "show_system_info": True
    }
}

def deep_merge(base, updates):
    """
    Recursively merge updates into base dict.
    WARNING: This function is vulnerable to prototype pollution-style attacks
    when processing untrusted input - similar to CVE-2022-41879
    """
    result = copy.deepcopy(base)
    for key, value in updates.items():
        if key == "__proto__" or key == "__class__":
            # These are handled specially - merged into parent context
            if isinstance(value, dict):
                for proto_key, proto_value in value.items():
                    result[proto_key] = proto_value
        elif isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def sanitize_response(data, config):
    """Remove sensitive fields based on denylist"""
    if isinstance(data, dict):
        sanitized = {}
        denylist = config.get("security", {}).get("keyword_denylist", [])
        for key, value in data.items():
            if key.lower() not in [k.lower() for k in denylist]:
                sanitized[key] = sanitize_response(value, config)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_response(item, config) for item in data]
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['GET'])
def get_info():
    """Public endpoint - returns system information"""
    return jsonify({
        "app": server_config["app_name"],
        "version": server_config["version"],
        "status": "operational",
        "endpoints": ["/api/webhooks", "/api/webhooks/<id>", "/api/config", "/api/trigger"]
    })

@app.route('/api/webhooks', methods=['GET'])
def list_webhooks():
    """List all registered webhooks"""
    webhooks = Webhook.objects()
    result = []
    for w in webhooks:
        webhook_data = {
            "id": str(w.id),
            "name": w.name,
            "url": w.url,
            "status": w.status,
            "created_at": w.created_at.isoformat() if w.created_at else None
        }
        result.append(sanitize_response(webhook_data, server_config))
    return jsonify({"webhooks": result})

@app.route('/api/webhooks/<webhook_id>', methods=['GET'])
def get_webhook(webhook_id):
    """Get webhook details by ID"""
    try:
        webhook = Webhook.objects(id=webhook_id).first()
        if not webhook:
            return jsonify({"error": "Webhook not found"}), 404
        
        webhook_data = {
            "id": str(webhook.id),
            "name": webhook.name,
            "url": webhook.url,
            "status": webhook.status,
            "config": webhook.config,
            "flag": webhook.flag,  # Sensitive field - should be filtered by denylist
            "created_at": webhook.created_at.isoformat() if webhook.created_at else None
        }
        return jsonify({"webhook": sanitize_response(webhook_data, server_config)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current server configuration (sanitized)"""
    safe_config = {
        "version": server_config["version"],
        "app_name": server_config["app_name"],
        "features": server_config["features"]
    }
    return jsonify({"config": safe_config})

@app.route('/api/trigger', methods=['POST'])
def trigger_webhook():
    """
    Trigger a webhook with payload processing.
    Accepts webhook response data and processes it with configuration overrides.
    
    This endpoint simulates receiving data from a Cloud Code webhook endpoint.
    The payload can include configuration updates that are merged with server config.
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.json
    webhook_id = data.get("webhook_id")
    payload = data.get("payload", {})
    config_updates = data.get("config_updates", {})
    
    if not webhook_id:
        return jsonify({"error": "webhook_id is required"}), 400
    
    try:
        webhook = Webhook.objects(id=webhook_id).first()
        if not webhook:
            return jsonify({"error": "Webhook not found"}), 404
        
        # VULNERABILITY: Merge config_updates into server_config
        # This allows prototype pollution-style bypass of security settings
        # Similar to CVE-2022-41879 in Parse Server
        effective_config = deep_merge(server_config, config_updates)
        
        # Process webhook data with the (potentially polluted) config
        webhook_data = {
            "id": str(webhook.id),
            "name": webhook.name,
            "url": webhook.url,
            "status": webhook.status,
            "config": webhook.config,
            "flag": webhook.flag,  # Contains the flag for admin webhook
            "payload_processed": payload
        }
        
        # Sanitize with effective config (denylist may have been bypassed!)
        result = sanitize_response(webhook_data, effective_config)
        
        return jsonify({
            "success": True,
            "webhook_response": result
        })
        
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

@app.route('/api/webhooks', methods=['POST'])
def create_webhook():
    """Create a new webhook registration"""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.json
    name = data.get("name")
    url = data.get("url")
    
    if not name or not url:
        return jsonify({"error": "name and url are required"}), 400
    
    webhook = Webhook(
        name=name,
        url=url,
        status="active",
        config=data.get("config", {})
    )
    webhook.save()
    
    return jsonify({
        "success": True,
        "webhook": {
            "id": str(webhook.id),
            "name": webhook.name,
            "url": webhook.url,
            "status": webhook.status
        }
    }), 201

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

def reset_database():
    flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
    
    # Clear existing data
    Webhook.drop_collection()
    SystemConfig.drop_collection()
    
    # Create sample webhooks
    Webhook(
        name="Notification Service",
        url="https://notify.internal.cloudsync.io/hook",
        status="active",
        config={"retry_count": 3, "timeout": 30}
    ).save()
    
    Webhook(
        name="Analytics Pipeline",
        url="https://analytics.internal.cloudsync.io/ingest",
        status="active",
        config={"batch_size": 100}
    ).save()
    
    Webhook(
        name="Backup Handler",
        url="https://backup.internal.cloudsync.io/snapshot",
        status="paused",
        config={"compression": True}
    ).save()
    
    # Admin webhook with flag - this is the target
    Webhook(
        name="System Controller",
        url="https://admin.internal.cloudsync.io/controller",
        status="active",
        config={"privileged": True, "admin_access": True},
        flag=flag
    ).save()
    
    # Store initial config
    SystemConfig(
        key="server_config",
        value=server_config
    ).save()

if __name__ == '__main__':
    reset_database()
    app.run(debug=False, host='0.0.0.0', port=5003)
