# encoding=utf8
# PinData Analytics Platform - Controller Service
# Version 0.9.2 (Pre-RBAC)

from flask import Flask, request, jsonify, Response
import os
import sys
import platform
import json
import datetime

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

# Load sensitive configuration including API keys
config_secret = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# Application metadata
APP_NAME = "PinData Analytics Platform"
APP_VERSION = "0.9.2"
COMPONENT = "controller"

# Simulated internal configuration (mimics Apache Pinot structure)
INTERNAL_CONFIG = {
    "zookeeper.path": "/pindata/CONTROLLER",
    "cluster.name": "PinDataCluster",
    "helix.controller.uri": "http://helix-controller:9998",
    "segment.store.uri": "hdfs://namenode:9000/pindata/segments",
    "controller.host": "controller-node-01",
    "controller.port": 9000,
    "controller.vip.host": "pindata-controller.internal",
    "controller.vip.port": 9000,
    "controller.data.dir": "/var/pindata/controller/data",
    "pinot.controller.startable.class": "org.apache.pindata.controller.ControllerStarter"
}


def get_index_content():
    """Generate the main dashboard HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PinData Analytics Platform</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
            .header { background: #16213e; padding: 20px; border-bottom: 3px solid #0f3460; }
            .header h1 { margin: 0; color: #e94560; }
            .header p { margin: 5px 0 0 0; color: #888; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .card { background: #16213e; border-radius: 8px; padding: 20px; margin: 20px 0; }
            .card h2 { color: #e94560; margin-top: 0; }
            .status { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; }
            .status-healthy { background: #2d6a4f; color: #b7e4c7; }
            .nav { list-style: none; padding: 0; margin: 20px 0; }
            .nav li { display: inline-block; margin-right: 20px; }
            .nav a { color: #e94560; text-decoration: none; }
            .nav a:hover { text-decoration: underline; }
            table { width: 100%; border-collapse: collapse; }
            th, td { text-align: left; padding: 12px; border-bottom: 1px solid #0f3460; }
            th { color: #e94560; }
            .endpoint { font-family: monospace; background: #0f3460; padding: 2px 6px; border-radius: 3px; }
            code { background: #0f3460; padding: 2px 6px; border-radius: 3px; font-size: 13px; }
            footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <h1>PinData Analytics Platform</h1>
                <p>Real-time Distributed OLAP Datastore - Controller v""" + APP_VERSION + """</p>
            </div>
        </div>
        <div class="container">
            <div class="card">
                <h2>System Status</h2>
                <p>Controller Status: <span class="status status-healthy">HEALTHY</span></p>
                <p>Cluster: """ + INTERNAL_CONFIG['cluster.name'] + """</p>
                <p>Component: """ + COMPONENT + """</p>
            </div>
            
            <div class="card">
                <h2>API Endpoints</h2>
                <table>
                    <tr><th>Endpoint</th><th>Description</th></tr>
                    <tr><td><code>/health</code></td><td>Health check endpoint</td></tr>
                    <tr><td><code>/api/v1/cluster/info</code></td><td>Basic cluster information</td></tr>
                    <tr><td><code>/api/v1/tables</code></td><td>List available tables</td></tr>
                    <tr><td><code>/api/v1/segments</code></td><td>Segment information</td></tr>
                </table>
            </div>
            
            <div class="card">
                <h2>Documentation</h2>
                <p>For full API documentation, visit the <a href="/swagger" style="color: #e94560;">Swagger UI</a>.</p>
                <p>Version: """ + APP_VERSION + """ | Build: 20240115-001</p>
            </div>
        </div>
        <footer>
            &copy; 2024 PinData Analytics Platform | Licensed under Apache 2.0
        </footer>
    </body>
    </html>
    """


@app.route('/')
def index():
    """Main dashboard"""
    return get_index_content()


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "HEALTHY",
        "component": COMPONENT,
        "version": APP_VERSION
    })


@app.route('/api/v1/cluster/info')
def cluster_info():
    """Basic cluster information - authenticated endpoint"""
    return jsonify({
        "clusterName": INTERNAL_CONFIG['cluster.name'],
        "controllerHost": INTERNAL_CONFIG['controller.vip.host'],
        "controllerPort": INTERNAL_CONFIG['controller.vip.port'],
        "status": "RUNNING"
    })


@app.route('/api/v1/tables')
def tables():
    """List available tables"""
    return jsonify({
        "tables": [
            {"name": "events_realtime", "type": "REALTIME", "status": "ONLINE"},
            {"name": "users_offline", "type": "OFFLINE", "status": "ONLINE"},
            {"name": "metrics_hybrid", "type": "HYBRID", "status": "ONLINE"}
        ]
    })


@app.route('/api/v1/segments')
def segments():
    """Segment information"""
    return jsonify({
        "segments": {
            "events_realtime": ["events_realtime_0", "events_realtime_1", "events_realtime_2"],
            "users_offline": ["users_offline_0"],
            "metrics_hybrid": ["metrics_hybrid_rt_0", "metrics_hybrid_offline_0"]
        }
    })


@app.route('/swagger')
def swagger():
    """Swagger documentation placeholder"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>PinData API Documentation</title></head>
    <body style="font-family: sans-serif; padding: 40px; background: #1a1a2e; color: #eee;">
        <h1 style="color: #e94560;">PinData API Documentation</h1>
        <p>API documentation is currently being generated.</p>
        <p>Available endpoints:</p>
        <ul>
            <li><code>/health</code> - Health check</li>
            <li><code>/api/v1/cluster/info</code> - Cluster information</li>
            <li><code>/api/v1/tables</code> - List tables</li>
            <li><code>/api/v1/segments</code> - Segment information</li>
            <li><code>/appconfigs</code> - Application configuration (internal)</li>
        </ul>
        <p><a href="/" style="color: #e94560;">Back to Dashboard</a></p>
    </body>
    </html>
    """


# VULNERABLE ENDPOINT: No authentication check
# This endpoint exposes sensitive application configuration
# including environment variables and internal secrets
# CVE-2024-27099 style vulnerability - missing RBAC
@app.route('/appconfigs')
def appconfigs():
    """
    Application configuration endpoint.
    WARNING: This endpoint exposes sensitive configuration data.
    In production, this should be protected by RBAC.
    """
    # Collect system information
    system_info = {
        "os.name": platform.system(),
        "os.version": platform.version(),
        "os.arch": platform.machine(),
        "java.version": "N/A (Python runtime)",
        "python.version": platform.python_version(),
        "user.name": os.environ.get('USER', 'pindata'),
        "user.dir": os.getcwd(),
        "user.home": os.environ.get('HOME', '/home/pindata')
    }
    
    # Collect JVM/Runtime information  
    runtime_info = {
        "runtime.max.memory": "512MB",
        "runtime.total.memory": "256MB",
        "runtime.free.memory": "128MB",
        "runtime.available.processors": os.cpu_count() or 1
    }
    
    # Collect environment variables (DANGEROUS - exposes secrets)
    env_config = {
        "PINDATA_CLUSTER": os.environ.get('PINDATA_CLUSTER', 'default'),
        "PINDATA_CONTROLLER_HOST": os.environ.get('APP_HOST', 'localhost'),
        "PINDATA_CONTROLLER_PORT": os.environ.get('APP_PORT', '5000'),
        "ZOOKEEPER_ADDRESS": os.environ.get('ZOOKEEPER_ADDRESS', 'zk-01.internal:2181'),
        "HELIX_CLUSTER_NAME": INTERNAL_CONFIG['cluster.name'],
        # This exposes the secret API key / flag
        "PINDATA_ADMIN_SECRET": config_secret
    }
    
    # Collect application configuration
    app_config = {
        "component": COMPONENT,
        "version": APP_VERSION,
        "config": INTERNAL_CONFIG
    }
    
    # Build the full response (mimics Apache Pinot's PinotAppConfigs)
    response = {
        "systemConfig": system_info,
        "runtimeConfig": runtime_info,
        "environmentConfig": env_config,
        "applicationConfig": app_config,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    
    return Response(
        json.dumps(response, indent=2),
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(debug=True)
