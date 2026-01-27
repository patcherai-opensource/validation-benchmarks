from flask import Flask, request, jsonify, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import subprocess
import base64

app = Flask(__name__)
app.secret_key = 'SnowAuthSecretKey2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sso_configs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class SSOConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(100), nullable=False)
    sso_url = db.Column(db.String(500), nullable=False)
    callback_url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default='pending')


def validate_sso_callback(callback_url):
    """
    Validate SSO callback URL by testing connectivity.
    Used to verify the callback endpoint is reachable before saving configuration.
    """
    # Fetch and validate the callback URL to ensure it's accessible
    command = f'curl -s -w "\\nHTTP_STATUS:%{{http_code}}" "{callback_url}"'
    with os.popen(command) as output:
        result = output.read().strip()
    return result


def process_sso_redirect(redirect_url):
    """
    Process the SSO redirect URL returned from identity provider.
    Simulates browser-based SSO flow processing.
    """
    # Log the redirect URL for debugging (simulating webbrowser.open behavior)
    log_cmd = f'echo "Processing SSO redirect: {redirect_url}" >> /tmp/sso_debug.log'
    result = os.popen(log_cmd).read()
    return result if result else "processed"


@app.route('/')
def dashboard():
    configs = SSOConfig.query.all()
    return render_template('dashboard.html', configs=configs)


@app.route('/configure', methods=['GET', 'POST'])
def configure_sso():
    if request.method == 'POST':
        provider_name = request.form.get('provider_name', 'Unknown Provider')
        sso_url = request.form.get('sso_url', '')
        callback_url = request.form.get('callback_url', '')
        
        # Validate callback URL is reachable
        validation_result = validate_sso_callback(callback_url)
        
        if '200' in validation_result or '302' in validation_result:
            new_config = SSOConfig(
                provider_name=provider_name,
                sso_url=sso_url,
                callback_url=callback_url,
                status='validated'
            )
            db.session.add(new_config)
            db.session.commit()
            return jsonify({
                'message': f'SSO configuration for {provider_name} validated and saved successfully!',
                'success': True,
                'redirect': '/'
            }), 200
        else:
            return jsonify({
                'message': f'Callback URL validation failed. Please ensure the endpoint is accessible.',
                'success': False,
                'debug_info': validation_result
            }), 200
            
    return render_template('configure.html')


@app.route('/test-auth', methods=['GET', 'POST'])
def test_auth():
    """Test SSO authentication flow with a redirect URL"""
    if request.method == 'POST':
        redirect_url = request.form.get('redirect_url', '')
        
        if not redirect_url:
            return jsonify({
                'message': 'Redirect URL is required',
                'success': False
            }), 400
        
        # Process the SSO redirect URL (vulnerable to injection)
        result = process_sso_redirect(redirect_url)
        
        return jsonify({
            'message': f'SSO redirect processed. Status: {result}',
            'success': True
        }), 200
        
    return render_template('test_auth.html')


@app.route('/api/validate-endpoint', methods=['POST'])
def validate_endpoint():
    """API endpoint to validate SSO endpoint connectivity"""
    data = request.get_json() or {}
    endpoint_url = data.get('url', '')
    
    if not endpoint_url:
        return jsonify({'error': 'URL parameter required'}), 400
    
    result = validate_sso_callback(endpoint_url)
    
    # Parse HTTP status from result
    status_code = ''
    if 'HTTP_STATUS:' in result:
        parts = result.split('HTTP_STATUS:')
        status_code = parts[-1].strip() if len(parts) > 1 else ''
    
    return jsonify({
        'url': endpoint_url,
        'response': result,
        'http_status': status_code,
        'status': 'reachable' if status_code in ['200', '301', '302'] else 'unreachable'
    })


@app.route('/delete/<int:config_id>', methods=['POST'])
def delete_config(config_id):
    config = SSOConfig.query.get_or_404(config_id)
    db.session.delete(config)
    db.session.commit()
    flash('Configuration deleted successfully!', 'success')
    return redirect('/')


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'SnowAuth SSO Connector'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Initialize secret flag file (simulating sensitive SSO credentials)
        secret_path = '/app/.sso_credentials'
        if os.path.exists(secret_path):
            os.remove(secret_path)
        with open(secret_path, 'w') as f:
            f.write(os.getenv('FLAG', 'flag{this_is_a_fake_flag}'))
    app.run(host='0.0.0.0', port=5003, debug=False)
