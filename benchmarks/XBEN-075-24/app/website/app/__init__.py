from flask import Flask, render_template_string
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DEBUG'] = False

error_template = '''
<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body>
<h1>{{ error_title }}</h1>
<p>{{ error_message }}</p>
</body>
</html>
'''

@app.errorhandler(404)
def not_found(e):
    return render_template_string(error_template, error_title="404 Not Found", error_message="The requested resource was not found."), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template_string(error_template, error_title="500 Internal Server Error", error_message="An internal error occurred."), 500

from app import routes
