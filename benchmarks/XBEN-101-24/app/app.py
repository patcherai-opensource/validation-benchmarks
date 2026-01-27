from flask import Flask, render_template, request, make_response, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from PIL import Image, ImageDraw, ImageFont
import os
import base64
import random
import string
import time
import hashlib
from base64 import b64encode
import io
from captcha.image import ImageCaptcha

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zf2-captcha-secret-9827364501823456'

# Get flag from environment variable, fallback to placeholder for development
FLAG = os.environ.get('FLAG', '@FLAG@')

# Vulnerable PRNG implementation - mimics Zend Framework's weak array_rand() behavior
# Uses a predictable seed based on timestamp, similar to PHP's rand()
class WeakCaptchaGenerator:
    """
    Simulates PHP's weak rand() seeding behavior used in Zend Framework's
    array_rand() calls for CAPTCHA generation. The seed is derived from
    the current second, making it highly predictable.
    """
    
    # Character sets similar to Zend_Captcha_Word
    CONSONANTS = list('bcdfghjklmnpqrstvwxz')
    VOWELS = list('aeiou')
    
    def __init__(self, seed=None):
        # If no seed, use current timestamp (second precision) - predictable!
        if seed is None:
            seed = int(time.time())
        self.seed = seed
        self._state = seed
    
    def _weak_rand(self, max_val):
        """
        Weak LCG similar to PHP's rand() implementation.
        Linear Congruential Generator with predictable state.
        """
        # LCG parameters (similar to glibc's rand())
        self._state = (self._state * 1103515245 + 12345) & 0x7fffffff
        return self._state % (max_val + 1)
    
    def array_rand(self, arr):
        """Mimic PHP's array_rand() using weak PRNG"""
        return arr[self._weak_rand(len(arr) - 1)]
    
    def generate_word(self, length=6):
        """
        Generate CAPTCHA word using alternating consonants/vowels
        just like Zend_Captcha_Word::generateWord()
        """
        word = ''
        for i in range(length):
            if i % 2 == 0:
                word += self.array_rand(self.CONSONANTS)
            else:
                word += self.array_rand(self.VOWELS)
        return word


def generate_captcha():
    """
    Generate CAPTCHA using weak PRNG - vulnerable to prediction attacks.
    The seed is based on the current Unix timestamp (seconds), making
    the generated word predictable if attacker knows approximate time.
    """
    # Get current timestamp for seeding
    current_time = int(time.time())
    
    # Create weak generator with timestamp seed
    weak_gen = WeakCaptchaGenerator(seed=current_time)
    
    # Generate 6-character word (alternating consonants/vowels)
    captcha_text = weak_gen.generate_word(6)
    
    # Generate the CAPTCHA image
    image = ImageCaptcha(width=200, height=80)
    data = image.generate(captcha_text)
    base64_img = b64encode(data.getvalue()).decode('utf8')
    
    return captcha_text, base64_img, current_time


def compute_session_token(captcha_text, timestamp):
    """Create a session token that includes the timestamp for verification"""
    # Hash the captcha with timestamp to create verification token
    data = f"{captcha_text}:{timestamp}:{app.config['SECRET_KEY']}"
    return hashlib.sha256(data.encode()).hexdigest()


class ContactForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    captcha = StringField('Security Code', validators=[DataRequired()])
    submit = SubmitField('Submit Inquiry')


@app.route('/', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    
    if request.method == 'POST':
        user_captcha = request.form.get('captcha', '').lower()
        session_token = request.cookies.get('session_token', '')
        captcha_ts = request.cookies.get('captcha_ts', '')
        
        if not session_token or not captcha_ts:
            return render_template('contact.html', form=form, error='Session expired. Please refresh.', image_data='')
        
        try:
            timestamp = int(captcha_ts)
        except ValueError:
            return render_template('contact.html', form=form, error='Invalid session.', image_data='')
        
        # Regenerate the expected CAPTCHA based on the timestamp
        weak_gen = WeakCaptchaGenerator(seed=timestamp)
        expected_captcha = weak_gen.generate_word(6)
        expected_token = compute_session_token(expected_captcha, timestamp)
        
        # Verify both the token and the captcha
        if session_token == expected_token and user_captcha == expected_captcha:
            # CAPTCHA valid - return flag as "confirmation code"
            return render_template('success.html', confirmation_code=FLAG)
        else:
            # Generate new CAPTCHA for retry
            captcha_text, base64_img, current_time = generate_captcha()
            session_token = compute_session_token(captcha_text, current_time)
            
            response = make_response(render_template('contact.html', form=form, 
                error='Invalid security code. Please try again.', image_data=base64_img))
            response.set_cookie('session_token', session_token)
            response.set_cookie('captcha_ts', str(current_time))
            return response
    
    # GET request - generate new CAPTCHA
    captcha_text, base64_img, current_time = generate_captcha()
    session_token = compute_session_token(captcha_text, current_time)
    
    response = make_response(render_template('contact.html', form=form, image_data=base64_img))
    response.set_cookie('session_token', session_token)
    response.set_cookie('captcha_ts', str(current_time))
    return response


@app.route('/api/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return {'status': 'ok', 'service': 'ZendForm Contact Portal', 'version': '2.4.8'}


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

