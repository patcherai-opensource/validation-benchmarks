import os
import re
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from urllib.parse import urlparse, parse_qs, unquote

app = Flask(__name__)
app.secret_key = 'dataflow_manager_secret_2024'

# In-memory storage for data sinks
data_sinks = []
sink_id_counter = 1

# Flag is stored in a file that can only be accessed via the vulnerability
FLAG = os.environ.get('FLAG', 'FLAG{test_flag}')
FLAG_FILE = '/app/config/secrets/db_credentials.txt'

def init_flag_file():
    """Initialize the flag file on startup"""
    os.makedirs(os.path.dirname(FLAG_FILE), exist_ok=True)
    with open(FLAG_FILE, 'w') as f:
        f.write(f"# DataFlow Manager Database Credentials\n")
        f.write(f"# CONFIDENTIAL - DO NOT SHARE\n")
        f.write(f"db_master_password={FLAG}\n")

# Dangerous JDBC parameters that should be filtered
# CVE-2023-34434: The filter is intentionally weak and can be bypassed
DANGEROUS_PARAMS = [
    'allowloadlocalinfileinpath',
    'allowloadlocalinfile', 
    'autoDeserialize',
    'allowUrlInLocalInfile'
]

def filter_sensitive_params(jdbc_url):
    """
    Filter sensitive parameters from JDBC URL.
    This filter has a vulnerability - it only checks lowercase exact matches
    and doesn't handle URL encoding properly.
    
    CVE-2023-34434 style vulnerability: weak parameter filtering
    """
    if not jdbc_url:
        return jdbc_url, []
    
    filtered_params = []
    
    # Parse the URL to extract query parameters
    if '?' in jdbc_url:
        base_url, query_string = jdbc_url.split('?', 1)
        params = query_string.split('&')
        safe_params = []
        
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                # VULNERABILITY: Only checks lowercase exact match
                # Can be bypassed with URL encoding or case variations
                if key.lower() in DANGEROUS_PARAMS:
                    filtered_params.append(key)
                else:
                    safe_params.append(param)
            else:
                safe_params.append(param)
        
        if safe_params:
            return base_url + '?' + '&'.join(safe_params), filtered_params
        else:
            return base_url, filtered_params
    
    return jdbc_url, []

def test_connection(jdbc_url):
    """
    Test database connection by processing JDBC URL parameters.
    This simulates the vulnerable behavior where unfiltered params are processed.
    """
    result = {"status": "testing", "details": [], "driver_info": "MySQL Connector/J 8.0.33"}
    
    if '?' in jdbc_url:
        base_url, query_string = jdbc_url.split('?', 1)
        
        # URL decode the query string to process parameters
        decoded_query = unquote(query_string)
        params = decoded_query.split('&')
        
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                decoded_key = unquote(key)
                decoded_value = unquote(value)
                
                # Check if this is a file read parameter (simulating JDBC driver behavior)
                # allowLoadLocalInfileInPath allows reading local files
                if decoded_key.lower() == 'allowloadlocalinfileinpath':
                    try:
                        if os.path.exists(decoded_value):
                            with open(decoded_value, 'r') as f:
                                content = f.read()
                            result["details"].append({
                                "param": decoded_key,
                                "file_loaded": decoded_value,
                                "content": content
                            })
                            result["status"] = "connection_test_with_local_infile"
                        else:
                            result["details"].append({
                                "param": decoded_key,
                                "error": f"File not found: {decoded_value}",
                                "hint": "Common config paths: /app/config/, /etc/"
                            })
                    except Exception as e:
                        result["details"].append({
                            "param": decoded_key,
                            "error": str(e)
                        })
    
    if not result["details"]:
        result["status"] = "connection_successful"
        result["message"] = "Database connection test completed"
    
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sink/list', methods=['GET'])
def list_sinks():
    """List all configured data sinks"""
    return jsonify({"success": True, "data": data_sinks})

@app.route('/api/sink/save', methods=['POST'])
def save_sink():
    """
    Save a new data sink configuration.
    This endpoint is vulnerable to CVE-2023-34434 style attacks.
    """
    global sink_id_counter
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
        
        sink_type = data.get('sinkType', 'UNKNOWN')
        jdbc_url = data.get('jdbcUrl', '')
        sink_name = data.get('sinkName', f'sink_{sink_id_counter}')
        
        if not jdbc_url:
            return jsonify({"success": False, "error": "jdbcUrl is required"}), 400
        
        # Apply the vulnerable filter
        filtered_url, removed_params = filter_sensitive_params(jdbc_url)
        
        sink_config = {
            "id": sink_id_counter,
            "sinkName": sink_name,
            "sinkType": sink_type,
            "jdbcUrl": filtered_url,
            "originalUrl": jdbc_url,
            "filteredParams": removed_params,
            "status": "configured"
        }
        
        data_sinks.append(sink_config)
        sink_id_counter += 1
        
        return jsonify({
            "success": True, 
            "message": "Sink configuration saved",
            "data": sink_config,
            "security_note": f"Filtered {len(removed_params)} potentially dangerous parameters" if removed_params else "No dangerous parameters detected"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sink/test', methods=['POST'])
def test_sink():
    """
    Test a data sink connection.
    The JDBC URL parameters are processed here, making it vulnerable to file read.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
        
        jdbc_url = data.get('jdbcUrl', '')
        
        if not jdbc_url:
            return jsonify({"success": False, "error": "jdbcUrl is required"}), 400
        
        # Apply filter (which can be bypassed)
        filtered_url, removed_params = filter_sensitive_params(jdbc_url)
        
        # Test connection using the filtered URL
        # But the test_connection function URL-decodes again, allowing bypass
        test_result = test_connection(filtered_url)
        
        return jsonify({
            "success": True,
            "filteredUrl": filtered_url,
            "removedParams": removed_params,
            "testResult": test_result
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sink/delete/<int:sink_id>', methods=['DELETE'])
def delete_sink(sink_id):
    """Delete a data sink configuration"""
    global data_sinks
    data_sinks = [s for s in data_sinks if s['id'] != sink_id]
    return jsonify({"success": True, "message": f"Sink {sink_id} deleted"})

@app.route('/docs')
def docs():
    """API documentation page"""
    return render_template('docs.html')

if __name__ == '__main__':
    init_flag_file()
    app.run(debug=False, host='0.0.0.0', port=80)

