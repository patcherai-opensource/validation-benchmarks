from flask import Flask, render_template, request, make_response, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
import os
import base64
import random
import string
from base64 import b64encode
from captcha.image import ImageCaptcha
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = '6473c2599d5871cae38105a6247d56e40db3321820d619bb'

FLAG = os.environ.get('FLAG', 'FLAG{placeholder}')

RSA_KEY = RSA.generate(2048)
RSA_PUBLIC_KEY = RSA_KEY.publickey()

def generate_captcha():
    image = ImageCaptcha(width=280, height=90)
    captcha_text = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    captcha_text_redacted = captcha_text[:4] + "...."
    data = image.generate(captcha_text_redacted)
    base64_img = b64encode(data.getvalue()).decode('utf8')
    return captcha_text, base64_img

def encrypt_captcha(captcha_text):
    cipher = PKCS1_OAEP.new(RSA_PUBLIC_KEY, hashAlgo=SHA256)
    ciphertext = cipher.encrypt(captcha_text.encode('utf-8'))
    return base64.b64encode(ciphertext).decode('utf-8')

def decrypt_captcha(encrypted_data):
    try:
        ciphertext = base64.b64decode(encrypted_data)
    except Exception:
        raise ValueError("Invalid base64 encoding")
    
    if len(ciphertext) != 256:
        raise ValueError("Invalid ciphertext length")
    
    cipher = PKCS1_OAEP.new(RSA_KEY, hashAlgo=SHA256)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext

class NewUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    captcha = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Create User')


@app.route('/', methods=['GET', 'POST'])
def home():
    form = NewUserForm()
    if request.method == 'POST':
        user_captcha = request.form.get('captcha', '')
        cookie_captcha = request.cookies.get('captcha')
        
        if not cookie_captcha:
            return 'Session expired. Please refresh.', 400
        
        try:
            decrypted = decrypt_captcha(cookie_captcha)
            if decrypted.decode('utf-8') == user_captcha:
                return FLAG
            else:
                return 'Invalid CAPTCHA!', 403
        except ValueError as e:
            error_msg = str(e)
            if "Incorrect decryption" in error_msg:
                return "Decryption failed", 400
            elif "Invalid base64" in error_msg:
                return "Invalid request format", 400
            elif "Invalid ciphertext length" in error_msg:
                return "Invalid request format", 400
            else:
                return "Processing error", 500
    else:
        captcha_text, base64_img = generate_captcha()
        encrypted_captcha = encrypt_captcha(captcha_text)
        response = make_response(render_template('home.html', form=form, image_data=base64_img))
        response.set_cookie('captcha', encrypted_captcha)
        return response


@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    encrypted_token = data.get('ciphertext')
    if not encrypted_token:
        return jsonify({'error': 'Missing ciphertext'}), 400
    
    try:
        ciphertext = base64.b64decode(encrypted_token)
    except Exception:
        return jsonify({'error': 'Invalid base64 encoding'}), 400
    
    if len(ciphertext) != 256:
        return jsonify({'error': 'Invalid ciphertext length'}), 400
    
    cipher = PKCS1_OAEP.new(RSA_KEY, hashAlgo=SHA256)
    start_time = time.perf_counter_ns()
    try:
        plaintext = cipher.decrypt(ciphertext)
        elapsed = time.perf_counter_ns() - start_time
        return jsonify({
            'status': 'success',
            'processing_time_ns': elapsed
        })
    except ValueError:
        elapsed = time.perf_counter_ns() - start_time
        return jsonify({
            'error': 'Decryption failed',
            'processing_time_ns': elapsed
        }), 400


@app.route('/api/public-key', methods=['GET'])
def get_public_key():
    pem = RSA_PUBLIC_KEY.export_key().decode('utf-8')
    n = RSA_PUBLIC_KEY.n
    e = RSA_PUBLIC_KEY.e
    return jsonify({
        'public_key_pem': pem,
        'n': hex(n),
        'e': hex(e),
        'key_size': RSA_KEY.size_in_bits()
    })


@app.errorhandler(404)
def not_found(e):
    return 'Not Found', 404

@app.errorhandler(500)
def server_error(e):
    return 'Internal Server Error', 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

