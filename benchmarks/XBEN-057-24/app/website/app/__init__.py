from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

INDEX_STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'indexes')
os.makedirs(INDEX_STORE, exist_ok=True)

from app import routes
