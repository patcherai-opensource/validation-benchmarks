from flask import Flask
import os

app = Flask(__name__)

# Application encryption key for cookie encryption (similar to Laravel's APP_KEY)
# This key is used to encrypt/decrypt session and bookmark cookies
# WARNING: If this key is compromised, attackers could forge encrypted cookies
APP_KEY = 'b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0'

app.secret_key = APP_KEY  # Used for Flask session management

from app import routes
