from flask import Flask, request, jsonify, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import urllib.request
import json
import subprocess

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sso_providers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class SSOProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    discovery_endpoint = db.Column(db.String(500), nullable=False)
    client_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='pending')
    auth_url = db.Column(db.String(500), nullable=True)


def fetch_sso_config(discovery_url):
    try:
        req = urllib.request.Request(
            discovery_url,
            headers={'User-Agent': 'SSOConnector/1.0', 'Accept': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        return None


def test_sso_url(sso_url):
    command = f'curl -s -o /dev/null -w "%{{http_code}}" "{sso_url}"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()


@app.route('/')
def index():
    providers = SSOProvider.query.all()
    return render_template('index.html', providers=providers)


@app.route('/providers')
def list_providers():
    providers = SSOProvider.query.all()
    return render_template('providers.html', providers=providers)


@app.route('/add_provider', methods=['GET', 'POST'])
def add_provider():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        discovery_endpoint = request.form.get('discovery_endpoint', '').strip()
        client_id = request.form.get('client_id', '').strip()
        
        if not name or not discovery_endpoint:
            return jsonify({'success': False, 'message': 'Name and Discovery Endpoint are required'}), 400
        
        provider = SSOProvider(
            name=name,
            discovery_endpoint=discovery_endpoint,
            client_id=client_id if client_id else None,
            status='pending'
        )
        db.session.add(provider)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'SSO Provider "{name}" added successfully',
            'redirect': '/providers'
        })
    
    return render_template('add_provider.html')


@app.route('/test_connection/<int:provider_id>', methods=['POST'])
def test_connection(provider_id):
    provider = SSOProvider.query.get_or_404(provider_id)
    
    config = fetch_sso_config(provider.discovery_endpoint)
    
    if not config:
        provider.status = 'error'
        db.session.commit()
        return jsonify({
            'success': False,
            'message': 'Failed to fetch SSO configuration from discovery endpoint'
        })
    
    sso_url = config.get('authorization_endpoint') or config.get('sso_url') or config.get('auth_url')
    
    if not sso_url:
        provider.status = 'invalid'
        db.session.commit()
        return jsonify({
            'success': False,
            'message': 'No authorization endpoint found in SSO configuration'
        })
    
    provider.auth_url = sso_url
    
    try:
        status_code = test_sso_url(sso_url)
        
        if status_code and status_code.startswith(('2', '3')):
            provider.status = 'active'
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'SSO Provider verified successfully. Auth endpoint returned status {status_code}'
            })
        else:
            provider.status = 'unreachable'
            db.session.commit()
            return jsonify({
                'success': False,
                'message': f'SSO auth endpoint returned status: {status_code}'
            })
    except Exception:
        provider.status = 'error'
        db.session.commit()
        return jsonify({
            'success': False,
            'message': 'Error testing SSO connection'
        })


@app.route('/delete_provider/<int:provider_id>', methods=['POST'])
def delete_provider(provider_id):
    provider = SSOProvider.query.get_or_404(provider_id)
    db.session.delete(provider)
    db.session.commit()
    flash('SSO Provider deleted successfully', 'success')
    return redirect('/providers')


@app.route('/api/provider/<int:provider_id>')
def get_provider(provider_id):
    provider = SSOProvider.query.get_or_404(provider_id)
    return jsonify({
        'id': provider.id,
        'name': provider.name,
        'discovery_endpoint': provider.discovery_endpoint,
        'client_id': provider.client_id,
        'status': provider.status,
        'auth_url': provider.auth_url
    })


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003)
