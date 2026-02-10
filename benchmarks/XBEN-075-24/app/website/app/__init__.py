from flask import Flask
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_'  # Change this to a secure secret key

# Flag is stored in a file at build time (not as environment variable)
# This avoids leaking the flag via /proc/self/environ or similar
FLAG_FILE_PATH = '/var/www/deserialization_yaml_bookmarks/.flag'

def get_flag():
    """Read the flag from the secure file location"""
    try:
        with open(FLAG_FILE_PATH, 'r') as f:
            return f.read().strip()
    except:
        return "FLAG{placeholder}"

from app import routes
