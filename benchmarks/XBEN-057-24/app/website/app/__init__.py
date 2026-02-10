from flask import Flask
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_modelhub_2024'  # Secret key for session

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

from app import routes
