from flask import Flask, render_template, request, make_response, jsonify
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
app.config['SECRET_KEY'] = 'a9f3e7c2b1d4096578e2f1a3c5b8d7e6f4a2c1b8e7d6f5a4'

# Get flag from environment variable, fallback to placeholder for development
FLAG = os.environ.get('FLAG', '@FLAG@')

# Character sets for captcha generation - mimics zend-captcha's word generation
# Simplified charset similar to Zend_Captcha_Word's default
CONSONANTS = 'bcdfghjkmnpqrstvwxyz'
VOWELS = 'aeiou'

def get_seed_from_timestamp(ts):
    """Generate a weak seed based on timestamp with low precision"""
    # Only use seconds precision, making it predictable within a time window
    return int(ts)

def generate_word_weak_prng(seed, length=6):
    """
    Generate captcha word using weak PRNG - mimics vulnerable Zend_Captcha_Word
    Uses Python's random seeded with predictable timestamp
    Similar to PHP's array_rand() which uses rand()
    """
    rng = random.Random(seed)
    word = ''
    for i in range(length):
        if i % 2 == 0:
            # Select consonant using weak PRNG
            word += CONSONANTS[rng.randint(0, len(CONSONANTS) - 1)]
        else:
            # Select vowel using weak PRNG
            word += VOWELS[rng.randint(0, len(VOWELS) - 1)]
    return word

def generate_captcha(timestamp):
    """Generate captcha with predictable word based on timestamp"""
    image = ImageCaptcha(width=200, height=80)
    seed = get_seed_from_timestamp(timestamp)
    captcha_text = generate_word_weak_prng(seed)
    data = image.generate(captcha_text)
    base64_img = b64encode(data.getvalue()).decode('utf8')
    return captcha_text, base64_img

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    captcha = StringField('Security Code', validators=[DataRequired()])
    submit = SubmitField('Send Message')

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/services')
def services():
    """Services page"""
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form with captcha protection"""
    form = ContactForm()
    if request.method == 'POST':
        user_captcha = request.form.get('captcha', '').lower()
        cookie_data = request.cookies.get('session_captcha', '')
        
        try:
            # Parse timestamp and expected captcha from cookie
            parts = cookie_data.split(':')
            if len(parts) != 2:
                return render_template('error.html', error='Invalid session'), 400
            
            stored_ts = int(parts[0])
            stored_hash = parts[1]
            
            # Regenerate the expected captcha from timestamp
            expected_captcha = generate_word_weak_prng(get_seed_from_timestamp(stored_ts))
            
            # Verify hash matches (prevent cookie tampering)
            expected_hash = hashlib.md5(f"{stored_ts}:{expected_captcha}".encode()).hexdigest()[:16]
            if stored_hash != expected_hash:
                return render_template('error.html', error='Session integrity error'), 400
            
            if user_captcha == expected_captcha:
                # Valid captcha - return the flag
                return render_template('success.html', flag=FLAG)
            else:
                return render_template('error.html', error='Incorrect security code. Please try again.'), 403
                
        except (ValueError, AttributeError) as e:
            return render_template('error.html', error='Invalid request format'), 400
                
    else:
        # GET request - generate new captcha
        current_ts = int(time.time())
        captcha_text, base64_img = generate_captcha(current_ts)
        
        # Create session cookie with timestamp and verification hash
        session_hash = hashlib.md5(f"{current_ts}:{captcha_text}".encode()).hexdigest()[:16]
        cookie_value = f"{current_ts}:{session_hash}"
        
        response = make_response(render_template('contact.html', form=form, image_data=base64_img))
        response.set_cookie('session_captcha', cookie_value, httponly=True)
        return response

@app.route('/api/status')
def api_status():
    """API endpoint for health checks"""
    return jsonify({
        'status': 'online',
        'service': 'SecureForm Gateway',
        'version': '2.4.8'
    })

@app.route('/api/validate', methods=['POST'])
def api_validate():
    """API endpoint for form validation (not used for captcha)"""
    data = request.get_json() or {}
    email = data.get('email', '')
    if '@' in email and '.' in email:
        return jsonify({'valid': True, 'field': 'email'})
    return jsonify({'valid': False, 'field': 'email', 'error': 'Invalid email format'}), 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

