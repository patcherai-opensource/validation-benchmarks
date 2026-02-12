"""
Portfolio Service Application
Functional routing with static resource serving.
"""

import os
import mimetypes
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, urlparse
from datetime import datetime, timezone
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s - %(message)s')
logger = logging.getLogger('o.s.web.servlet.DispatcherServlet')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_LOCATION = os.path.join(BASE_DIR, 'static')


def process_path(path):
    """Process and sanitize the resource path."""
    if not path:
        return path

    path = path.lstrip('/')
    path = path.replace('\\', '/')

    return path


def is_invalid_path(path):
    """Check if the path contains invalid sequences."""
    if not path:
        return True

    if path.startswith('../') or path == '..':
        return True

    upper = path.upper()
    if upper.startswith('WEB-INF') or upper.startswith('META-INF'):
        return True

    return False


def resolve_resource(base_location, path):
    """Resolve a resource path relative to the base location."""
    resolved = os.path.join(base_location, path)
    resolved = os.path.normpath(resolved)
    return resolved


def timestamp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + '000Z'


def json_response(data):
    return json.dumps(data, indent=None, separators=(',', ':')).encode('utf-8')


class RequestHandler(BaseHTTPRequestHandler):
    server_version = ''
    sys_version = ''

    def log_message(self, format, *args):
        logger.info(format % args)

    def send_json(self, status, data):
        body = json_response(data)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file_response(self, filepath):
        mimetype = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
        with open(filepath, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', mimetype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        self.wfile.write(data)

    def send_error_json(self, status, error_text):
        self.send_json(status, {
            "timestamp": timestamp(),
            "status": status,
            "error": error_text,
            "path": self.path
        })

    def handle_health(self):
        self.send_json(200, {"status": "UP"})

    def handle_index(self):
        index_path = os.path.join(RESOURCE_LOCATION, 'index.html')
        if os.path.isfile(index_path):
            self.send_file_response(index_path)
        else:
            self.send_error_json(404, "Not Found")

    def handle_api_team(self):
        team = [
            {"id": 1, "name": "John", "role": "Senior Software Engineer",
             "experience": "20+ years", "specialization": "Full-stack development"},
            {"id": 2, "name": "Peter", "role": "Principal Engineer",
             "experience": "18+ years", "specialization": "Legacy systems modernization"}
        ]
        self.send_json(200, {"_embedded": {"members": team}, "_links": {"self": {"href": "/api/v1/team"}}})

    def handle_api_projects(self):
        projects = [
            {"id": 1, "name": "NAS (Not A Software)",
             "description": "A pioneering project from the early 2000s",
             "status": "MAINTAINED", "startDate": "2001-03-15"},
            {"id": 2, "name": "Modernizer 200",
             "description": "Innovative solution for modernizing legacy systems",
             "status": "ACTIVE", "startDate": "2022-07-01"}
        ]
        self.send_json(200, {"_embedded": {"projects": projects}, "_links": {"self": {"href": "/api/v1/projects"}}})

    def handle_actuator_health(self):
        self.send_json(200, {
            "status": "UP",
            "components": {
                "diskSpace": {"status": "UP", "details": {"total": 53687091200, "free": 41489448960, "threshold": 10485760}},
                "ping": {"status": "UP"}
            }
        })

    def handle_actuator_info(self):
        self.send_json(200, {
            "app": {"name": "portfolio-service", "version": "2.1.0", "description": "Portfolio Service Application"}
        })

    def handle_resource(self):
        """Serve static resources from the configured resource location."""
        raw_path = self.path
        prefix = '/resources/'
        idx = raw_path.find(prefix)
        if idx == -1:
            self.send_error_json(404, "Not Found")
            return

        # Extract the part after /resources/
        relative = raw_path[idx + len(prefix):]

        # Strip query string if present
        if '?' in relative:
            relative = relative[:relative.index('?')]

        # Decode URL-encoded characters
        decoded_path = unquote(relative)

        # Process and validate the path
        processed = process_path(decoded_path)

        if is_invalid_path(processed):
            self.send_error_json(400, "Bad Request")
            return

        # Resolve resource relative to location
        resource_file = resolve_resource(RESOURCE_LOCATION, processed)

        # Check if resource exists and is readable
        if os.path.isfile(resource_file):
            self.send_file_response(resource_file)
            return

        self.send_error_json(404, "Not Found")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Route requests
        if path == '/ping':
            self.handle_health()
        elif path == '/' or path == '':
            self.handle_index()
        elif path == '/api/v1/team':
            self.handle_api_team()
        elif path == '/api/v1/projects':
            self.handle_api_projects()
        elif path == '/actuator/health':
            self.handle_actuator_health()
        elif path == '/actuator/info':
            self.handle_actuator_info()
        elif path.startswith('/resources/'):
            self.handle_resource()
        else:
            self.send_error_json(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/v1/contact':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''

            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self.send_error_json(400, "Bad Request")
                return

            name = data.get('name', '')
            email = data.get('email', '')
            message = data.get('message', '')

            if not all([name, email, message]):
                self.send_json(400, {"error": "Bad Request", "message": "name, email, and message are required"})
                return

            self.send_json(202, {
                "status": "ACCEPTED",
                "message": "Thank you for contacting us",
                "timestamp": timestamp()
            })
        else:
            self.send_error_json(404, "Not Found")

    def do_HEAD(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/ping' or path == '/' or path == '':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


def run_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    logger.info("Starting Portfolio Service on port %d", port)
    logger.info("Static resources served from: %s", RESOURCE_LOCATION)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == '__main__':
    run_server()
