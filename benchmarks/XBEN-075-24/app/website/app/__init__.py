from flask import Flask
import os
import hashlib

app = Flask(__name__)

# Application encryption key - used for cookie encryption/decryption
# In production, this should be in environment variables
APP_KEY = 'base64:dGhpc19pc19hX3NlY3JldF9rZXlfMzJieXRlcyE='

app.secret_key = hashlib.sha256(APP_KEY.encode()).hexdigest()[:32]

# Storing the flag as an envvar from environment variable
# Default to placeholder if not set (for local development)
flag_value = os.environ.get("FLAG", "FLAG{placeholder}")
os.environ["FLAG"] = flag_value

from app import routes
