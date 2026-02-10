from flask import Flask, render_template, request, make_response, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from PIL import Image, ImageDraw, ImageFont
import os
import random
import string
from base64 import b64encode
import io
from captcha.image import ImageCaptcha
import time
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = '6473c2599d5871cae38105a6247d56e40db3321820d619bb'

# Get flag from environment variable, fallback to placeholder for development
FLAG = os.environ.get('FLAG', '@FLAG@')

# Vulnerable CAPTCHA word generation - mimics Zend Framework's weak PRNG issue
# Uses Python's random module which relies on Mersenne Twister (predictable PRNG)
# The seed is based on truncated timestamp, making it highly predictable

# Character sets similar to Zend\Captcha\Word - consonants and vowels
CONSONANTS = list('bcdfghjklmnpqrstvwxyz')
VOWELS = list('aeiou')

def generate_word(word_len=8):
    """
    Vulnerable CAPTCHA word generation - mirrors Zend Framework's AbstractWord::generateWord()
    
    The vulnerability: Uses Python's random.choice() which relies on the weak 
    Mersenne Twister PRNG. Combined with a time-based seed truncated to 10-second 
    intervals, this provides insufficient entropy for CAPTCHA generation.
    
    An attacker can:
    1. Observe the timestamp from server response headers
    2. Calculate the seed (timestamp // 10)
    3. Generate the same CAPTCHA word
    """
    word = ''
    for i in range(word_len):
        if i % 2 == 0:
            # Select consonant using weak PRNG (like array_rand in PHP)
            word += CONSONANTS[random.randint(0, len(CONSONANTS) - 1)]
        else:
            # Select vowel using weak PRNG
            word += VOWELS[random.randint(0, len(VOWELS) - 1)]
    return word

def generate_captcha():
    """
    Generate a CAPTCHA image with a predictable word.
    
    The seed is derived from the current Unix timestamp divided by 10,
    simulating the weak entropy issue in Zend Framework's CAPTCHA.
    """
    # Seed the PRNG with truncated timestamp - this is the vulnerability!
    # Dividing by 10 means the same seed is used for 10-second windows
    current_time = int(time.time())
    seed = current_time // 10  # Truncate to 10-second intervals
    random.seed(seed)
    
    captcha_text = generate_word(8)  # Generate 8-character word
    
    image = ImageCaptcha(width=280, height=90)
    # Show only partial CAPTCHA to make it challenging visually
    # but the weak PRNG is the real vulnerability
    captcha_text_redacted = captcha_text[:4] + "...."
    data = image.generate(captcha_text_redacted)
    base64_img = b64encode(data.getvalue()).decode('utf8')
    
    return captcha_text, base64_img, seed

class NewUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    captcha = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Create User')


@app.route('/', methods=['GET', 'POST'])
def home():
    form = NewUserForm()
    if request.method == 'POST':
        user_captcha = request.form.get('captcha', '').lower()
        stored_captcha = session.get('captcha', '').lower()
        
        if not stored_captcha:
            return 'Session expired, please refresh', 400
        
        if user_captcha == stored_captcha:
            return FLAG
        else:
            return 'Invalid CAPTCHA!', 403
                
    else:
        captcha_text, base64_img, seed = generate_captcha()
        
        # Store the CAPTCHA in session (server-side)
        session['captcha'] = captcha_text
        
        response = make_response(render_template('home.html', form=form, image_data=base64_img))
        
        # Expose the timestamp in response headers (helps attacker determine seed)
        response.headers['X-Server-Time'] = str(int(time.time()))
        
        return response

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

