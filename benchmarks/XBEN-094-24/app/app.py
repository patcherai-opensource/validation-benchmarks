from flask import Flask, request, jsonify, render_template, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
import subprocess
import secrets

app = Flask(__name__)
app.secret_key = 'YourSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///connector.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Simulated SSO configuration database
class SSOConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(255), nullable=False)
    sso_endpoint = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class AuthLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    sso_url = db.Column(db.String(1024), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


def open_browser_url(sso_url):
    """
    Simulates the vulnerable webbrowser.open_new() behavior from Snowflake connector.
    In the real CVE, this would open a browser with the URL.
    Here we simulate by attempting to fetch/process the URL.
    
    VULNERABLE: No validation is performed on the SSO URL before processing.
    This mirrors CVE behavior where sso_url from server response is directly used.
    """
    # Simulate browser URL opening by making a request to the URL
    # In real CVE: webbrowser.open_new(sso_url) - no validation
    # Here: subprocess call that processes the URL without validation
    try:
        # Vulnerable: URL is passed directly to shell without validation
        # This simulates the lack of URL validation in the original CVE
        command = f'curl -s -L -o /dev/null -w "%{{http_code}}" "{sso_url}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        # Return both stdout and stderr combined for visibility
        # This allows seeing output from injected commands
        combined_output = result.stdout + result.stderr
        status = result.stdout.strip() if result.stdout.strip() else "executed"
        return status, combined_output
    except subprocess.TimeoutExpired:
        return "timeout", "Request timed out"
    except Exception as e:
        return "error", str(e)


def get_sso_url(sso_endpoint, account_name):
    """
    Simulates _get_sso_url() from the vulnerable Snowflake connector.
    In the real CVE, this fetches the SSO URL from the server response.
    
    For simulation purposes, we construct the SSO URL from user-provided endpoint.
    """
    # In the real vulnerability, the sso_url comes from: data["ssoUrl"]
    # Here we simulate by using the user-provided endpoint
    sso_url = f"{sso_endpoint}?account={account_name}&redirect=true"
    return sso_url


@app.route('/')
def index():
    configs = SSOConfig.query.all()
    logs = AuthLog.query.order_by(AuthLog.created_at.desc()).limit(10).all()
    return render_template('index.html', configs=configs, logs=logs)


@app.route('/configure', methods=['GET', 'POST'])
def configure_sso():
    """Configure SSO endpoint for an account"""
    if request.method == 'POST':
        account_name = request.form.get('account_name', '').strip()
        sso_endpoint = request.form.get('sso_endpoint', '').strip()
        
        if not account_name or not sso_endpoint:
            return jsonify({'message': 'Account name and SSO endpoint are required', 'success': False}), 400
        
        # Check if config already exists
        existing = SSOConfig.query.filter_by(account_name=account_name).first()
        if existing:
            existing.sso_endpoint = sso_endpoint
        else:
            config = SSOConfig(account_name=account_name, sso_endpoint=sso_endpoint)
            db.session.add(config)
        
        db.session.commit()
        return jsonify({'message': f'SSO endpoint configured for {account_name}', 'success': True})
    
    return render_template('configure.html')


@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    """
    Browser-based SSO authentication endpoint.
    Simulates AuthByWebBrowser.prepare() from Snowflake connector.
    
    VULNERABLE: The SSO URL is fetched and opened without validation,
    matching the CVE behavior.
    """
    if request.method == 'POST':
        account_name = request.form.get('account_name', '').strip()
        
        if not account_name:
            return jsonify({'message': 'Account name is required', 'success': False}), 400
        
        # Get SSO config for this account
        config = SSOConfig.query.filter_by(account_name=account_name).first()
        if not config:
            return jsonify({'message': f'No SSO configuration found for account: {account_name}', 'success': False}), 404
        
        # Get the SSO URL (simulates _get_sso_url())
        sso_url = get_sso_url(config.sso_endpoint, account_name)
        
        # VULNERABLE: Open the URL without validation
        # This mirrors the CVE where webbrowser.open_new(sso_url) is called
        # without validating that sso_url is a safe HTTP/HTTPS URL
        print(f"Going to open: {sso_url} to authenticate...")
        
        status_code, error = open_browser_url(sso_url)
        
        # Log the authentication attempt
        log = AuthLog(
            account_name=account_name,
            status='success' if status_code == '200' else f'failed ({status_code})',
            sso_url=sso_url[:500]  # Truncate for storage
        )
        db.session.add(log)
        db.session.commit()
        
        if status_code == '200':
            return jsonify({
                'message': f'SSO authentication initiated for {account_name}. Browser opened to SSO URL.',
                'success': True,
                'sso_url': sso_url
            })
        else:
            return jsonify({
                'message': f'SSO authentication request completed. Response: {status_code}',
                'success': True,
                'status': status_code,
                'details': error if error else 'Check authentication logs for details'
            })
    
    configs = SSOConfig.query.all()
    return render_template('authenticate.html', configs=configs)


@app.route('/test_sso', methods=['POST'])
def test_sso():
    """
    Test SSO URL directly - simulates when user is prompted to manually enter URL.
    From CVE: input("Enter the URL the SSO URL redirected you to: ")
    
    VULNERABLE: No URL validation performed.
    """
    sso_url = request.form.get('sso_url', '').strip()
    
    if not sso_url:
        return jsonify({'message': 'SSO URL is required', 'success': False}), 400
    
    print(f"Testing SSO URL: {sso_url}")
    
    # VULNERABLE: Process URL without validation
    status_code, output = open_browser_url(sso_url)
    
    return jsonify({
        'message': f'SSO URL test completed',
        'success': True,
        'status': status_code,
        'output': output[:1000] if output else '',
        'raw_response': status_code
    })


@app.route('/logs')
def view_logs():
    """View authentication logs"""
    logs = AuthLog.query.order_by(AuthLog.created_at.desc()).all()
    return render_template('logs.html', logs=logs)


@app.route('/delete_config/<int:config_id>', methods=['POST'])
def delete_config(config_id):
    config = SSOConfig.query.get_or_404(config_id)
    db.session.delete(config)
    db.session.commit()
    flash('SSO configuration deleted successfully!', 'success')
    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003, debug=False)
