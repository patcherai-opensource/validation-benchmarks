import os
import sys

# Ensure the environment variables from Apache are passed through
def application(environ, start_response):
    # Pass through FLAG environment variable
    if 'FLAG' in environ:
        os.environ['FLAG'] = environ['FLAG']
    
    # Import the Flask app
    from app import app
    return app(environ, start_response)
