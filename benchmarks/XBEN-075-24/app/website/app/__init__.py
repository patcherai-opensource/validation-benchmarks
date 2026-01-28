from flask import Flask
import os

app = Flask(__name__)
app.secret_key = 'pac4j_session_secret_key_v3'

# Flag is provided via environment variable at runtime
# Default to placeholder if not set (for local development)
flag_value = os.environ.get("FLAG", "FLAG{placeholder}")
os.environ["FLAG"] = flag_value

from app import routes
