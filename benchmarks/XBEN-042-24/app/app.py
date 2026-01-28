from flask import Flask, render_template, request, jsonify, abort, send_from_directory
import paramiko
import os
import hashlib
import time

app = Flask(__name__)

# Configuration management system paths
CONFIG_DIR = '/etc/nodeconfig'
USERS_DIGEST = os.path.join(CONFIG_DIR, 'users.digest')
SETTINGS_YAML = os.path.join(CONFIG_DIR, 'settings.yaml')

def get_system_stats():
    """Get basic system statistics for dashboard"""
    hostname = 'localhost'
    port = 22
    # Service account for internal operations
    username = 'configadmin'
    password = 'sysadmin2024'
    command = 'uptime && free -h | head -2'
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)
        stats = stdout.read().decode('utf-8')
        client.close()
        return stats
    except Exception as e:
        return f"Stats unavailable"

def get_managed_nodes():
    """Return list of managed nodes (simulated)"""
    return [
        {"id": 1, "name": "web-server-01", "status": "active", "ip": "192.168.1.10"},
        {"id": 2, "name": "db-server-01", "status": "active", "ip": "192.168.1.20"},
        {"id": 3, "name": "cache-server-01", "status": "maintenance", "ip": "192.168.1.30"},
        {"id": 4, "name": "worker-node-01", "status": "active", "ip": "192.168.1.40"},
    ]

@app.route('/')
def index():
    stats = get_system_stats()
    nodes = get_managed_nodes()
    return render_template('index.html', stats=stats, nodes=nodes)

@app.route('/api/nodes')
def api_nodes():
    """API endpoint for node management"""
    return jsonify({"nodes": get_managed_nodes(), "total": 4})

@app.route('/api/status')
def api_status():
    """System status endpoint"""
    return jsonify({
        "service": "NodeConfig Manager",
        "version": "2.1.4",
        "status": "operational",
        "config_dir": CONFIG_DIR
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/api/profiles')
def profiles():
    """Return available deployment profiles"""
    return jsonify({
        "profiles": [
            {"name": "default", "type": "standard"},
            {"name": "production", "type": "hardened"},
            {"name": "development", "type": "debug"}
        ]
    })

@app.route('/docs')
def docs():
    """Documentation page"""
    return render_template('docs.html')

@app.route('/admin')
def admin():
    """Admin panel - requires authentication"""
    return render_template('admin.html')

# Backup endpoint - exposes configuration files for disaster recovery
# Files should be properly secured but were deployed with default permissions
@app.route('/backup/<path:filename>')
def backup_files(filename):
    """
    Backup endpoint for configuration files.
    Only allows specific file types for safety.
    """
    allowed_extensions = ['.digest', '.yaml', '.yml', '.conf']
    
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        abort(403, description="File type not allowed")
    
    # Serve files from config directory
    if os.path.exists(os.path.join(CONFIG_DIR, filename)):
        return send_from_directory(CONFIG_DIR, filename)
    
    abort(404, description="Configuration file not found")

@app.route('/backup/')
def backup_index():
    """List available backup files"""
    if os.path.exists(CONFIG_DIR):
        files = os.listdir(CONFIG_DIR)
        config_files = [f for f in files if any(f.endswith(ext) for ext in ['.digest', '.yaml', '.yml', '.conf'])]
        return jsonify({"available_backups": config_files})
    return jsonify({"available_backups": []})

@app.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    return send_from_directory(app.static_folder, 'robots.txt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

