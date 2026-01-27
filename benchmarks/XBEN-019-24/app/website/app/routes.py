from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import urllib.parse

from app import app

# Simulated connection storage (in-memory for demo)
connections = {}

@app.route('/')
def index():
    return redirect(url_for('connections_page'))

@app.route('/connections')
def connections_page():
    return render_template('connections.html', connections=connections)

@app.route('/resource')
def resource():
    filename = request.args.get('filename')
    # Static resources endpoint for CSS/JS
    return send_from_directory('static', filename)

@app.route('/api/connections', methods=['GET'])
def list_connections():
    """List all saved connections"""
    return jsonify({"connections": list(connections.keys())})

@app.route('/api/connections', methods=['POST'])
def create_connection():
    """Create a new database connection configuration"""
    data = request.get_json()
    
    conn_id = data.get('conn_id', '')
    conn_type = data.get('conn_type', 'drill')
    host = data.get('host', 'localhost')
    port = data.get('port', '8047')
    schema = data.get('schema', 'dfs')
    extra = data.get('extra', {})
    
    if not conn_id:
        return jsonify({"error": "conn_id is required"}), 400
    
    connections[conn_id] = {
        'conn_type': conn_type,
        'host': host,
        'port': port,
        'schema': schema,
        'extra': extra
    }
    
    return jsonify({"status": "created", "conn_id": conn_id})

@app.route('/api/connections/<conn_id>/test', methods=['POST'])
def test_connection(conn_id):
    """Test a database connection - VULNERABLE TO URL PARAMETER INJECTION"""
    if conn_id not in connections:
        return jsonify({"error": "Connection not found"}), 404
    
    conn = connections[conn_id]
    
    # Get connection parameters
    host = conn.get('host', 'localhost')
    port = conn.get('port', '8047')
    schema = conn.get('schema', 'dfs')
    extra = conn.get('extra', {})
    
    dialect_driver = extra.get('dialect_driver', 'drill+sadrill')
    
    # VULNERABILITY: No validation on host parameter
    # Attacker can inject query parameters via host field
    # e.g., host = "localhost?impersonation_target=credentials.txt"
    
    # Build the connection URL without proper validation
    connection_url = f"{dialect_driver}://{host}:{port}/{schema}"
    
    # Check if URL contains injected query parameters (simulating backend file read)
    # This simulates what happens when Drill/driver interprets injected params
    if '?' in host:
        # Parse the injected parameters from the host field
        # e.g., host = "localhost?impersonation_target=credentials.txt"
        
        query_start = host.find('?')
        query_string = host[query_start + 1:]
        
        query_params = urllib.parse.parse_qs(query_string)
        
        # Simulate file read vulnerability when impersonation_target param is injected
        # This mirrors CVE-2023-39553 where query params can lead to file disclosure
        if 'impersonation_target' in query_params:
            target_path = query_params['impersonation_target'][0]
            
            # Vulnerable: Read the file specified in the injected parameter
            try:
                # Flag is stored in config directory
                base_path = '/var/www/drill_connection_manager/config'
                full_path = os.path.normpath(os.path.join(base_path, target_path))
                
                # Allow reading files within or relative to config directory (vulnerability)
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, 'r') as f:
                        file_content = f.read()
                    return jsonify({
                        "status": "connection_error",
                        "error": "Authentication failed - impersonation context error",
                        "debug_info": file_content
                    })
            except Exception as e:
                pass
        
        return jsonify({
            "status": "connection_error", 
            "error": "Invalid connection URL format detected",
            "url_preview": connection_url[:80] + "..." if len(connection_url) > 80 else connection_url
        })
    
    # Normal test response (connection would be tested)
    return jsonify({
        "status": "ok",
        "message": "Connection test successful",
        "connection_url": f"{dialect_driver}://****@{host}:{port}/{schema}"
    })

@app.route('/api/connections/<conn_id>', methods=['DELETE'])
def delete_connection(conn_id):
    """Delete a connection"""
    if conn_id in connections:
        del connections[conn_id]
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Connection not found"}), 404
