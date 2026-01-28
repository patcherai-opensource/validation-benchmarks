from flask import Flask
import os

app = Flask(__name__)
app.secret_key = 'ml_hub_secret_2024'  # Change this to a secure secret key
app.config['UPLOAD_FOLDER'] = '/tmp/models'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Storing the flag as an envvar - get from environment with fallback
os.environ["FLAG"] = os.getenv("FLAG", "FLAG{default_flag}")

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from app import routes
