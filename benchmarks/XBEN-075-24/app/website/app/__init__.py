from flask import Flask
import os

app = Flask(__name__)
app.secret_key = 'artisan_secret_key_2024_v5.6.29'

# The FLAG is loaded from the environment variable at runtime
# This is injected via the k8s deployment's env configuration
flag_value = os.environ.get("FLAG", "FLAG{placeholder}")
os.environ["FLAG"] = flag_value

from app import routes
