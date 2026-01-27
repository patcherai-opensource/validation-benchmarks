# Data Analytics Processing Service
# Accepts serialized data objects for processing

from flask import Flask, request, jsonify, render_template_string, render_template, redirect, url_for, make_response
import pickle
import base64
import os
import hashlib

app = Flask(__name__)

# Session management
sessions = {}

def generate_session_id():
    return hashlib.md5(os.urandom(16)).hexdigest()

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Main dashboard for the data analytics service"""
    session_cookie = request.cookies.get('session_data')
    
    user_data = None
    if session_cookie:
        try:
            # Deserialize session data from cookie
            # This uses pickle to restore user preferences and session state
            decoded = base64.b64decode(session_cookie)
            user_data = pickle.loads(decoded)
        except Exception as e:
            user_data = {"error": f"Failed to load session: {str(e)}"}
    
    return render_template('dashboard.html', user_data=user_data)

@app.route('/analytics', methods=['POST'])
def process_analytics():
    """Process analytics data payload"""
    data_payload = request.form.get('data_payload')
    
    if not data_payload:
        return jsonify({"status": "error", "message": "No data payload provided"}), 400
    
    try:
        # Deserialize the analytics data for processing
        # Uses pickle for object serialization format support
        decoded = base64.b64decode(data_payload)
        analytics_obj = pickle.loads(decoded)
        
        result = {
            "status": "success",
            "message": "Data processed successfully",
            "processed_type": str(type(analytics_obj).__name__),
            "processed_data": str(analytics_obj)[:200]
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Processing failed: {str(e)}"}), 400

@app.route('/import', methods=['GET', 'POST'])
def import_data():
    """Import serialized data configurations"""
    if request.method == 'GET':
        return render_template('import.html')
    
    # Handle file upload of serialized config
    if 'config_file' in request.files:
        config_file = request.files['config_file']
        if config_file.filename != '':
            try:
                file_content = config_file.read()
                # Deserialize configuration object
                config_obj = pickle.loads(file_content)
                return jsonify({
                    "status": "success", 
                    "message": "Configuration imported",
                    "config_type": str(type(config_obj).__name__)
                })
            except Exception as e:
                return jsonify({"status": "error", "message": f"Import failed: {str(e)}"}), 400
    
    return jsonify({"status": "error", "message": "No file provided"}), 400

@app.route('/export', methods=['GET'])
def export_sample():
    """Export a sample serialized configuration"""
    sample_config = {
        "version": "1.0",
        "analytics_settings": {
            "retention_days": 30,
            "aggregation_level": "daily"
        }
    }
    serialized = base64.b64encode(pickle.dumps(sample_config)).decode('utf-8')
    return jsonify({
        "status": "success",
        "sample_config_b64": serialized,
        "note": "Base64 encoded pickle format"
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "service": "DataFlow Analytics Engine",
        "version": "2.4.1",
        "status": "operational",
        "serialization_format": "pickle",
        "encoding": "base64"
    })

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
