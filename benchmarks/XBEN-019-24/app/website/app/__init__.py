from flask import Flask

app = Flask(__name__, static_folder=None)

from app import routes

