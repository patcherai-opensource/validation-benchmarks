from flask import Flask

app = Flask(__name__, static_folder=None)
app.config['PROPAGATE_EXCEPTIONS'] = False

from app import routes

