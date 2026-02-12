"""
uWSGI-compatible HTTP server with PHP plugin emulation.

This server implements the same request routing logic as the uWSGI PHP plugin,
including docroot-based file resolution and PHP CGI execution.

Configuration is loaded from /etc/uwsgi/uwsgi.ini.
"""

import http.server
import os
import subprocess
import mimetypes
import urllib.parse
import configparser
import sys
import signal
import io

# Load configuration
config = configparser.ConfigParser()
config.read('/etc/uwsgi/uwsgi.ini')

uwsgi_section = config['uwsgi'] if 'uwsgi' in config else {}
DOCUMENT_ROOT = uwsgi_section.get('php-docroot', '/var/www/html')
ALLOWED_DOCROOT = uwsgi_section.get('php-allowed-docroot', None)
PHP_INDEX = uwsgi_section.get('php-index', 'index.php')
LISTEN_PORT = int(uwsgi_section.get('http-port', '80'))
SERVER_NAME = uwsgi_section.get('server-name', 'uwsgi')
STATIC_EXPIRES = int(uwsgi_section.get('static-expires', '3600'))

# MIME type initialization
mimetypes.init()


def resolve_php_path(document_root, path_info):
    """
    Resolve a request path against the document root.
    
    This follows the uWSGI PHP plugin logic:
    1. Concatenate document_root + "/" + path_info
    2. Use os.path.realpath to resolve symlinks and normalize
    3. Check against allowed_docroot if configured
    
    Returns the resolved absolute path or None if not found.
    """
    # Concatenate document_root with path_info (matching uwsgi_concat4n behavior)
    raw_path = os.path.join(document_root, path_info.lstrip('/'))
    
    # Resolve the real path (equivalent to realpath() in C)
    real_path = os.path.realpath(raw_path)
    
    # Check if file exists
    if not os.path.exists(real_path):
        return None
    
    # If allowed_docroot is configured, enforce the containment check
    if ALLOWED_DOCROOT is not None:
        allowed = os.path.realpath(ALLOWED_DOCROOT)
        if not real_path.startswith(allowed + '/') and real_path != allowed:
            return None
    
    return real_path


def execute_php(script_path, env_vars):
    """Execute a PHP script via php-cgi and return the output."""
    env = os.environ.copy()
    env.update(env_vars)
    env['SCRIPT_FILENAME'] = script_path
    env['REDIRECT_STATUS'] = '200'
    
    try:
        result = subprocess.run(
            ['php-cgi'],
            env=env,
            capture_output=True,
            timeout=30
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return b'Status: 504\r\n\r\nGateway Timeout'
    except Exception:
        return b'Status: 500\r\n\r\nInternal Server Error'


class UWSGIRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler emulating uWSGI PHP plugin behavior."""
    
    server_version = 'uWSGI/2.0.15'
    sys_version = ''
    
    def log_message(self, format, *args):
        """Suppress request logging to stderr."""
        pass
    
    def send_error_page(self, code, message=''):
        """Send a minimal error response."""
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        body = f'<html><body><h1>{code}</h1><p>{message}</p></body></html>'
        self.wfile.write(body.encode())
    
    def handle_request(self, method='GET'):
        """Main request handling logic following uWSGI PHP plugin flow."""
        # Parse the URL
        parsed = urllib.parse.urlparse(self.path)
        path_info = urllib.parse.unquote(parsed.path)
        query_string = parsed.query
        
        # Resolve the file path using uWSGI's docroot logic
        resolved_path = resolve_php_path(DOCUMENT_ROOT, path_info)
        
        # If path resolves to a directory, try index file
        if resolved_path and os.path.isdir(resolved_path):
            index_path = os.path.join(resolved_path, PHP_INDEX)
            if os.path.isfile(index_path):
                resolved_path = index_path
            else:
                self.send_error_page(403, 'Forbidden')
                return
        
        if resolved_path is None or not os.path.isfile(resolved_path):
            self.send_error_page(404, 'Not Found')
            return
        
        # Check if it's a PHP file
        if resolved_path.endswith('.php'):
            self.serve_php(resolved_path, path_info, query_string, method)
        else:
            self.serve_static(resolved_path)
    
    def serve_php(self, script_path, path_info, query_string, method):
        """Execute and serve a PHP file."""
        content_type = self.headers.get('Content-Type', '')
        content_length = self.headers.get('Content-Length', '0')
        
        # Read POST body if present
        body = b''
        if method == 'POST':
            try:
                body_len = int(content_length)
                body = self.rfile.read(body_len)
            except (ValueError, IOError):
                body = b''
        
        env_vars = {
            'GATEWAY_INTERFACE': 'CGI/1.1',
            'SERVER_SOFTWARE': f'uWSGI/2.0.15',
            'SERVER_NAME': SERVER_NAME,
            'SERVER_PORT': str(LISTEN_PORT),
            'SERVER_PROTOCOL': self.request_version,
            'REQUEST_METHOD': method,
            'PATH_INFO': path_info,
            'SCRIPT_NAME': path_info,
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': content_type,
            'CONTENT_LENGTH': str(len(body)),
            'DOCUMENT_ROOT': DOCUMENT_ROOT,
            'REQUEST_URI': self.path,
            'HTTP_HOST': self.headers.get('Host', 'localhost'),
            'HTTP_USER_AGENT': self.headers.get('User-Agent', ''),
            'HTTP_ACCEPT': self.headers.get('Accept', ''),
            'HTTP_COOKIE': self.headers.get('Cookie', ''),
            'REMOTE_ADDR': self.client_address[0],
        }
        
        # Write POST body to stdin for php-cgi
        if body:
            env_vars['CONTENT_LENGTH'] = str(len(body))
        
        env = os.environ.copy()
        env.update(env_vars)
        env['SCRIPT_FILENAME'] = script_path
        env['REDIRECT_STATUS'] = '200'
        
        try:
            result = subprocess.run(
                ['php-cgi'],
                env=env,
                input=body,
                capture_output=True,
                timeout=30
            )
            output = result.stdout
        except Exception:
            self.send_error_page(500, 'Internal Server Error')
            return
        
        # Parse CGI headers from php-cgi output
        header_end = output.find(b'\r\n\r\n')
        if header_end == -1:
            header_end = output.find(b'\n\n')
            if header_end == -1:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(output)
                return
            separator_len = 2
        else:
            separator_len = 4
        
        headers_raw = output[:header_end].decode('utf-8', errors='replace')
        body_content = output[header_end + separator_len:]
        
        status_code = 200
        response_headers = {}
        for line in headers_raw.split('\n'):
            line = line.strip()
            if line.lower().startswith('status:'):
                try:
                    status_code = int(line.split(':', 1)[1].strip().split(' ')[0])
                except ValueError:
                    pass
            elif ':' in line:
                key, val = line.split(':', 1)
                response_headers[key.strip()] = val.strip()
        
        self.send_response(status_code)
        for key, val in response_headers.items():
            if key.lower() != 'status':
                self.send_header(key, val)
        if 'Content-Type' not in response_headers:
            self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(body_content)))
        self.end_headers()
        self.wfile.write(body_content)
    
    def serve_static(self, file_path):
        """Serve a static file."""
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', f'max-age={STATIC_EXPIRES}')
            self.end_headers()
            self.wfile.write(content)
        except PermissionError:
            self.send_error_page(403, 'Forbidden')
        except IOError:
            self.send_error_page(404, 'Not Found')
    
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def do_HEAD(self):
        self.handle_request('GET')


def run_server():
    """Start the HTTP server."""
    server = http.server.HTTPServer(('0.0.0.0', LISTEN_PORT), UWSGIRequestHandler)
    
    def handle_signal(signum, frame):
        server.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    server.serve_forever()


if __name__ == '__main__':
    run_server()
