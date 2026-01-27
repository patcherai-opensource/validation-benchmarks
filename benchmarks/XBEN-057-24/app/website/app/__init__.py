from flask import Flask
import os

app = Flask(__name__)

# Application encryption key - used for cookie encryption (similar to Laravel APP_KEY)
# WARNING: This key should never be exposed publicly!
APP_KEY = 'base64:dGhpc2lzYXNlY3JldGtleWZvcmVuY3J5cHRpb24xMjM0'

app.secret_key = APP_KEY
app.config['APP_KEY'] = APP_KEY

# Storing the flag as an envvar - get from environment with fallback
os.environ["FLAG"] = os.getenv("FLAG", "FLAG{default_flag}")

from app import routes
