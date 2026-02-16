import os
import re
import hashlib
import urllib.request
import urllib.error
import json
import socket
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, abort

app = Flask(__name__)
app.secret_key = hashlib.sha256(b'axis-service-mgmt-2024').hexdigest()

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

users = {
    ADMIN_USERNAME: {
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD,
        'role': 'administrator',
        'display_name': 'System Administrator',
        'email': 'admin@axis-services.local'
    }
}

service_registry = {
    'VersionService': {
        'name': 'VersionService',
        'provider': 'java:RPC',
        'class_name': 'org.apache.axis.Version',
        'status': 'running',
        'endpoint': 'http://localhost/services/Version',
        'allowed_methods': 'getVersion'
    },
    'AdminService': {
        'name': 'AdminService',
        'provider': 'java:MSG',
        'class_name': 'org.apache.axis.utils.Admin',
        'status': 'running',
        'endpoint': 'http://localhost/services/AdminService',
        'allowed_methods': 'AdminService'
    }
}

BLOCKED_SCHEMES = [
    'file', 'gopher', 'ftp', 'data', 'javascript',
    'ldap', 'ldaps', 'rmi', 'jms', 'jmx',
    'jrmp', 'java', 'dns', 'nis'
]

BLOCKED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '::1',
    '0.0.0.0'
]

def read_flag():
    try:
        with open('/app/config/deployment-key.conf', 'r') as f:
            return f.read().strip()
    except Exception:
        return 'FLAG_NOT_SET'

def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        user = users.get(session['username'])
        if not user or user.get('role') != 'administrator':
            abort(403)
        return f(*args, **kwargs)
    return decorated

def validate_registry_uri(uri):
    if not uri:
        return False, "Empty URI"
    
    scheme_match = re.match(r'^([a-zA-Z][a-zA-Z0-9+\-.]*):\/\/', uri)
    if not scheme_match:
        return False, "Invalid URI format"
    
    scheme = scheme_match.group(1).lower()

    for blocked in BLOCKED_SCHEMES:
        if scheme == blocked:
            return False, "Protocol '{}' is not permitted for security reasons".format(scheme)
    
    host_match = re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*:\/\/([^/:]+)', uri)
    if host_match:
        host = host_match.group(1).lower()
        for blocked_host in BLOCKED_HOSTS:
            if host == blocked_host:
                return False, "Access to host '{}' is restricted".format(host)
    
    return True, None

@app.route('/')
def index():
    if 'username' in session:
        user = users.get(session['username'])
        if user and user.get('role') == 'administrator':
            return redirect(url_for('dashboard'))
        return redirect(url_for('console'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '')
        display_name = request.form.get('display_name', username)

        if not username or not password:
            flash('Username and password are required.')
        elif username in users:
            flash('Username already exists.')
        elif username.lower() == 'admin':
            flash('Reserved username.')
        else:
            users[username] = {
                'username': username,
                'password': password,
                'role': 'operator',
                'display_name': display_name,
                'email': email
            }
            flash('Account created. Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/console')
@require_login
def console():
    user = users.get(session['username'])
    services = list(service_registry.values())
    return render_template('console.html', user=user, services=services)

@app.route('/dashboard')
@require_admin
def dashboard():
    user = users.get(session['username'])
    services = list(service_registry.values())
    return render_template('dashboard.html', user=user, services=services)

@app.route('/services/list')
@require_login
def services_list():
    return jsonify({
        'services': [
            {'name': s['name'], 'status': s['status'], 'provider': s['provider']}
            for s in service_registry.values()
        ]
    })

@app.route('/services/<service_name>/wsdl')
@require_login
def service_wsdl(service_name):
    svc = service_registry.get(service_name)
    if not svc:
        abort(404)
    wsdl_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    name="{name}" targetNamespace="http://axis.apache.org/{name}">
  <wsdl:service name="{name}">
    <wsdl:port name="{name}Port" binding="tns:{name}Binding">
      <soap:address location="{endpoint}"/>
    </wsdl:port>
  </wsdl:service>
</wsdl:definitions>'''.format(name=svc['name'], endpoint=svc['endpoint'])
    return Response(wsdl_xml, mimetype='text/xml')

@app.route('/admin/services/configure', methods=['GET', 'POST'])
@require_admin
def configure_service():
    result = None
    error = None

    if request.method == 'POST':
        service_name = request.form.get('service_name', '').strip()
        registry_uri = request.form.get('registry_uri', '').strip()
        action = request.form.get('action', 'lookup')

        if not service_name:
            error = "Service name is required"
        elif not registry_uri:
            error = "Registry URI is required"
        else:
            valid, validation_error = validate_registry_uri(registry_uri)
            if not valid:
                error = "Registry URI validation failed: {}".format(validation_error)
            else:
                try:
                    req = urllib.request.Request(registry_uri, method='GET')
                    req.add_header('User-Agent', 'AxisServiceBroker/1.3')
                    req.add_header('Accept', 'text/xml, application/xml, application/soap+xml')
                    resp = urllib.request.urlopen(req, timeout=5)
                    response_data = resp.read().decode('utf-8', errors='replace')

                    if action == 'lookup':
                        result = {
                            'status': 'success',
                            'service': service_name,
                            'registry_response': response_data[:4096],
                            'response_code': resp.getcode()
                        }
                    elif action == 'register':
                        service_registry[service_name] = {
                            'name': service_name,
                            'provider': 'java:RPC',
                            'class_name': 'custom.{}'.format(service_name),
                            'status': 'registered',
                            'endpoint': registry_uri,
                            'allowed_methods': '*'
                        }
                        result = {
                            'status': 'registered',
                            'service': service_name,
                            'endpoint': registry_uri
                        }
                except urllib.error.HTTPError as e:
                    body = ''
                    try:
                        body = e.read().decode('utf-8', errors='replace')[:2048]
                    except Exception:
                        pass
                    result = {
                        'status': 'error',
                        'response_code': e.code,
                        'registry_response': body
                    }
                except urllib.error.URLError as e:
                    error = "Failed to reach registry endpoint: {}".format(str(e.reason))
                except socket.timeout:
                    error = "Connection to registry timed out"
                except Exception as e:
                    error = "Registry lookup failed: {}".format(type(e).__name__)

    user = users.get(session['username'])
    services = list(service_registry.values())
    return render_template('configure.html', user=user, services=services,
                           result=result, error=error)

@app.route('/admin/services/<service_name>/control', methods=['POST'])
@require_admin
def control_service(service_name):
    svc = service_registry.get(service_name)
    if not svc:
        abort(404)
    cmd = request.form.get('cmd')
    if cmd == 'start':
        svc['status'] = 'running'
    elif cmd == 'stop':
        svc['status'] = 'stopped'
    elif cmd == 'restart':
        svc['status'] = 'running'
    flash('Service {} {}'.format(service_name, cmd))
    return redirect(url_for('dashboard'))

@app.route('/internal/deployment-descriptor')
def deployment_descriptor():
    if request.remote_addr not in ('127.0.0.1', '::1'):
        abort(403)
    flag = read_flag()
    descriptor = '''<?xml version="1.0" encoding="UTF-8"?>
<deployment name="internalConfig"
    xmlns="http://xml.apache.org/axis/wsdd/"
    xmlns:java="http://xml.apache.org/axis/wsdd/providers/java">
  <globalConfiguration>
    <parameter name="deploymentKey" value="{key}"/>
    <parameter name="disablePrettyXML" value="true"/>
    <parameter name="enableNamespacePrefixOptimization" value="false"/>
  </globalConfiguration>
  <handler type="java:org.apache.axis.handlers.http.URLMapper" name="URLMapper"/>
  <transport name="http">
    <requestFlow>
      <handler type="URLMapper"/>
    </requestFlow>
  </transport>
</deployment>'''.format(key=flag)
    return Response(descriptor, mimetype='text/xml')

@app.route('/admin/wsdd')
@require_admin
def wsdd_config():
    config_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<deployment name="defaultClientConfig"
    xmlns="http://xml.apache.org/axis/wsdd/"
    xmlns:java="http://xml.apache.org/axis/wsdd/providers/java">
  <globalConfiguration>
    <parameter name="disablePrettyXML" value="true"/>
    <parameter name="dotNetSoapEncFix" value="true"/>
    <parameter name="enableNamespacePrefixOptimization" value="false"/>
    <requestFlow>
      <handler type="java:org.apache.axis.handlers.JWSHandler">
        <parameter name="scope" value="session"/>
      </handler>
    </requestFlow>
  </globalConfiguration>
  <handler type="java:org.apache.axis.handlers.http.URLMapper" name="URLMapper"/>
  <handler type="java:org.apache.axis.handlers.SimpleAuthenticationHandler" name="Authenticate"/>
  <service name="AdminService" provider="java:MSG">
    <namespace>http://xml.apache.org/axis/wsdd/</namespace>
    <parameter name="allowedMethods" value="AdminService"/>
    <parameter name="enableRemoteAdmin" value="false"/>
    <parameter name="className" value="org.apache.axis.utils.Admin"/>
    <parameter name="internalDescriptorPath" value="/internal/deployment-descriptor"/>
  </service>
  <service name="VersionService" provider="java:RPC">
    <parameter name="allowedMethods" value="getVersion"/>
    <parameter name="className" value="org.apache.axis.Version"/>
  </service>
  <transport name="http">
    <requestFlow>
      <handler type="URLMapper"/>
      <handler type="java:org.apache.axis.handlers.http.HTTPAuthHandler"/>
    </requestFlow>
  </transport>
</deployment>'''
    return Response(config_xml, mimetype='text/xml')

@app.route('/services/Version')
def version_service():
    version_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <getVersionResponse>
      <getVersionReturn>Apache Axis version: 1.3</getVersionReturn>
    </getVersionResponse>
  </soapenv:Body>
</soapenv:Envelope>'''
    return Response(version_xml, mimetype='text/xml')

@app.route('/ping')
def ping():
    return 'OK', 200

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access Denied'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Not Found'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message='Internal Server Error'), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
