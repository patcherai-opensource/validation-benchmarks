import os
from flask import Flask

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')
os.makedirs(UPLOAD_DIR, exist_ok=True)

from app import routes
