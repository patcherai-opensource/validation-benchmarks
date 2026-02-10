from flask import Flask
import os

app = Flask(__name__)

app.config['APP_KEY'] = 'base64:dGhpc19pc19hX3NlY3JldF9rZXlfZm9yX2VuY3J5cHRpb24='

from app import routes
