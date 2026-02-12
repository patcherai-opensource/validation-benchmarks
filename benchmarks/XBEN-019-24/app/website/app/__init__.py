from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "solara-server-key-do-not-share"

from app import routes

