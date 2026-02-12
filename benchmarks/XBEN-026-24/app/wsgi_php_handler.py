import os
import subprocess
import mimetypes

DOCUMENT_ROOT = os.environ.get("UWSGI_PHP_DOCROOT", "/var/www/html")
PHP_INDEX = "index.php"
PHP_BINARY = "/usr/bin/php-cgi"

mimetypes.init()


def get_content_type(filepath):
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type if mime_type else "application/octet-stream"


def serve_static_file(filepath, start_response):
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        content_type = get_content_type(filepath)
        start_response('200 OK', [
            ('Content-Type', content_type),
            ('Content-Length', str(len(content))),
        ])
        return [content]
    except IOError:
        return None


def execute_php(filepath, environ, start_response):
    cgi_env = {
        'SCRIPT_FILENAME': filepath,
        'SCRIPT_NAME': environ.get('PATH_INFO', '/'),
        'REQUEST_METHOD': environ.get('REQUEST_METHOD', 'GET'),
        'QUERY_STRING': environ.get('QUERY_STRING', ''),
        'CONTENT_TYPE': environ.get('CONTENT_TYPE', ''),
        'CONTENT_LENGTH': environ.get('CONTENT_LENGTH', ''),
        'SERVER_NAME': environ.get('SERVER_NAME', 'localhost'),
        'SERVER_PORT': environ.get('SERVER_PORT', '80'),
        'SERVER_PROTOCOL': environ.get('SERVER_PROTOCOL', 'HTTP/1.1'),
        'DOCUMENT_ROOT': DOCUMENT_ROOT,
        'REDIRECT_STATUS': '200',
        'HTTP_HOST': environ.get('HTTP_HOST', 'localhost'),
        'PATH': '/usr/local/bin:/usr/bin:/bin',
    }

    stdin_data = b''
    if environ.get('REQUEST_METHOD') == 'POST':
        try:
            length = int(environ.get('CONTENT_LENGTH', 0))
            if length > 0:
                stdin_data = environ['wsgi.input'].read(length)
        except (ValueError, KeyError):
            pass

    try:
        result = subprocess.run(
            [PHP_BINARY],
            env=cgi_env,
            input=stdin_data,
            capture_output=True,
            timeout=10
        )

        output = result.stdout
        header_end = output.find(b'\r\n\r\n')
        sep_len = 4
        if header_end == -1:
            header_end = output.find(b'\n\n')
            sep_len = 2
            if header_end == -1:
                start_response('200 OK', [('Content-Type', 'text/html')])
                return [output]

        raw_headers = output[:header_end].decode('utf-8', errors='replace')
        body = output[header_end + sep_len:]

        headers = []
        status = '200 OK'
        for line in raw_headers.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                k, v = key.strip(), value.strip()
                if k.lower() == 'status':
                    status = v
                else:
                    headers.append((k, v))

        if not any(h[0].lower() == 'content-type' for h in headers):
            headers.append(('Content-Type', 'text/html'))

        start_response(status, headers)
        return [body]

    except subprocess.TimeoutExpired:
        start_response('504 Gateway Timeout', [('Content-Type', 'text/html')])
        return [b'<html><body><h1>504 Gateway Timeout</h1></body></html>']
    except Exception:
        start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
        return [b'<html><body><h1>500 Internal Server Error</h1></body></html>']


def resolve_filename(path_info):
    """Construct and resolve the filesystem path for a given request path."""
    if path_info.startswith('/'):
        filename = DOCUMENT_ROOT + path_info
    else:
        filename = DOCUMENT_ROOT + "/" + path_info
    return os.path.realpath(filename)


def application(environ, start_response):
    path_info = environ.get('PATH_INFO', '/')

    real_filename = resolve_filename(path_info)

    if os.path.isdir(real_filename):
        index_path = os.path.join(real_filename, PHP_INDEX)
        if os.path.isfile(index_path):
            real_filename = index_path
        else:
            start_response('403 Forbidden', [('Content-Type', 'text/html')])
            return [b'<html><body><h1>403 Forbidden</h1></body></html>']

    if not os.path.isfile(real_filename):
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<html><body><h1>404 Not Found</h1></body></html>']

    if real_filename.endswith('.php'):
        return execute_php(real_filename, environ, start_response)

    result = serve_static_file(real_filename, start_response)
    if result is not None:
        return result

    start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
    return [b'<html><body><h1>500 Internal Server Error</h1></body></html>']
