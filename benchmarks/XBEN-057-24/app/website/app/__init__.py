from flask import Flask
import os
import base64
from cryptography.fernet import Fernet

app = Flask(__name__)

# Application encryption key - similar to Laravel's APP_KEY
# This key is used to encrypt/decrypt cookie values
# WARNING: Keep this secret in production!
APP_KEY = "dGhpc2lzYXNlY3JldGtleWZvcmVuY3J5cHRpb24xMjM0"  # base64 encoded 32-byte key

# Generate a valid Fernet key from APP_KEY
def get_fernet_key():
    # Use the APP_KEY to derive a Fernet-compatible key
    key_bytes = base64.urlsafe_b64decode(APP_KEY + "==")[:32]
    # Pad or trim to 32 bytes
    key_bytes = key_bytes.ljust(32, b'\x00')[:32]
    return base64.urlsafe_b64encode(key_bytes)

FERNET_KEY = get_fernet_key()
cipher_suite = Fernet(FERNET_KEY)

# Flag is stored in a file at build time (not as env var)
FLAG_FILE = "/var/www/deserialization_pickle_bookmarks/flag.txt"

def get_flag():
    try:
        with open(FLAG_FILE, 'r') as f:
            return f.read().strip()
    except:
        return "FLAG{default_flag}"

from app import routes
