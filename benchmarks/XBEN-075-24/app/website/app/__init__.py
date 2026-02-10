from flask import Flask

app = Flask(__name__)
app.secret_key = 'your_secret_key_'

APP_KEY = 'base64:kT9Xp2mNvHj3qL8wRzY5bC6dF4eG1aI0'

from app import routes
