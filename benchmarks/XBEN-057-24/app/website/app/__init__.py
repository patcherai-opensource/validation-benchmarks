from flask import Flask
from datetime import timedelta
import json
import os

app = Flask(__name__,
            static_folder=os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'static'))

app.secret_key = os.urandom(32).hex()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.config['VERSION_NUMBER'] = '0.8.4'
app.config['LANGUAGES'] = {
    'lang_en': 'English',
    'lang_es': 'Spanish',
    'lang_fr': 'French',
    'lang_de': 'German',
    'lang_pt': 'Portuguese',
    'lang_ja': 'Japanese',
    'lang_zh': 'Chinese',
}
app.config['REGIONS'] = {
    '': 'Any',
    'us': 'United States',
    'gb': 'United Kingdom',
    'de': 'Germany',
    'fr': 'France',
    'jp': 'Japan',
}

from app import routes
