from flask import Flask

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

from app import routes

