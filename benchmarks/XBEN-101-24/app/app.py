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
import io
from captcha.image import ImageCaptcha
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a7f9e3c4d8b21a6e5f0c9d8e7b4a3f2e1d0c9b8a7f6e5d4c'

# Get flag from environment variable, fallback to placeholder for development
FLAG = os.environ.get('FLAG', '@FLAG@')

# Generate RSA key pair with fixed seed for CTF reproducibility
# This ensures the key is consistent across restarts for the challenge
from Crypto.Random import get_random_bytes
import hashlib

# Use a deterministic seed for the RSA key generation
# In production this would be insecure, but for CTF we need reproducibility
_SEED = hashlib.sha256(b"secureauth-ctf-challenge-2024").digest()
random.seed(int.from_bytes(_SEED, 'big'))

RSA_KEY = RSA.generate(2048)
RSA_PUBLIC_KEY = RSA_KEY.publickey()

# Reset random to non-deterministic for verification codes
random.seed()

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choice(string.digits) for _ in range(6))

def generate_captcha_image(code):
    """Generate a captcha image with the code partially obscured"""
    image = ImageCaptcha(width=200, height=70)
    # Only show first 3 digits in the image
    display_code = code[:3] + "***"
    data = image.generate(display_code)
    base64_img = b64encode(data.getvalue()).decode('utf8')
    return base64_img

def encrypt_token(plaintext):
    """Encrypt token using RSA-OAEP"""
    cipher = PKCS1_OAEP.new(RSA_PUBLIC_KEY, hashAlgo=SHA256)
    ciphertext = cipher.encrypt(plaintext.encode('utf-8'))
    return base64.b64encode(ciphertext).decode('utf-8')

def decrypt_token(token_b64):
    """
    Decrypt token using RSA-OAEP
    VULNERABLE: Non-constant-time error handling leaks padding information
    """
    try:
        ciphertext = base64.b64decode(token_b64)
    except Exception:
        raise ValueError("Invalid base64 encoding")
    
    # Check ciphertext length
    key_size_bytes = RSA_KEY.size_in_bytes()
    if len(ciphertext) != key_size_bytes:
        raise ValueError("Invalid ciphertext length")
    
    # Perform RSA decryption (modular exponentiation)
    c_int = int.from_bytes(ciphertext, 'big')
    m_int = pow(c_int, RSA_KEY.d, RSA_KEY.n)
    em = m_int.to_bytes(key_size_bytes, 'big')
    
    # VULNERABLE OAEP decoding - non-constant-time with distinguishable errors
    # This mimics the vulnerable PyCryptodome behavior
    
    # em = 0x00 || maskedSeed || maskedDB
    if em[0] != 0x00:
        # First byte must be 0x00
        raise ValueError("OAEP decoding error: invalid first byte")
    
    hash_len = 32  # SHA-256 output length
    
    # Split into components
    masked_seed = em[1:1+hash_len]
    masked_db = em[1+hash_len:]
    
    # MGF1 to recover seed and DB
    def mgf1(seed, length):
        result = b''
        counter = 0
        while len(result) < length:
            c = counter.to_bytes(4, 'big')
            result += SHA256.new(seed + c).digest()
            counter += 1
        return result[:length]
    
    seed_mask = mgf1(masked_db, hash_len)
    seed = bytes(a ^ b for a, b in zip(masked_seed, seed_mask))
    
    db_mask = mgf1(seed, len(masked_db))
    db = bytes(a ^ b for a, b in zip(masked_db, db_mask))
    
    # db = lHash || PS || 0x01 || M
    # where lHash = SHA256(""), PS = zero padding
    l_hash_expected = SHA256.new(b"").digest()
    l_hash = db[:hash_len]
    
    # VULNERABLE: Different error for hash mismatch vs padding issue
    if l_hash != l_hash_expected:
        raise ValueError("OAEP decoding error: label hash mismatch")
    
    # Find the 0x01 separator - VULNERABLE: non-constant-time search
    rest = db[hash_len:]
    separator_pos = -1
    for i, byte in enumerate(rest):
        if byte == 0x01:
            separator_pos = i
            break
        elif byte != 0x00:
            # VULNERABLE: Different error for invalid padding byte
            raise ValueError("OAEP decoding error: invalid padding byte")
    
    if separator_pos == -1:
        raise ValueError("OAEP decoding error: separator not found")
    
    plaintext = rest[separator_pos + 1:]
    return plaintext.decode('utf-8')

class VerificationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    verification_code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Verify Account')


# Additional routes to add noise/complexity for reconnaissance
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "SecureAuth API v2.1"})

@app.route('/api/public-key', methods=['GET'])
def get_public_key():
    """Expose public key for clients to encrypt data"""
    pem = RSA_PUBLIC_KEY.export_key().decode('utf-8')
    return jsonify({
        "algorithm": "RSA-OAEP",
        "hash": "SHA-256",
        "key_size": 2048,
        "public_key": pem
    })

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """Simple API documentation"""
    return jsonify({
        "endpoints": {
            "/": "Main verification form",
            "/api/health": "Service health check",
            "/api/public-key": "Get RSA public key for encryption",
            "/api/verify": "POST - Submit verification token",
            "/api/status": "GET - Check verification status",
            "/api/decrypt-test": "POST - Debug endpoint (internal use only)"
        },
        "version": "2.1.3",
        "crypto_library": "pycryptodome"
    })

@app.route('/api/status', methods=['GET'])
def status():
    """Check verification session status"""
    session_token = request.cookies.get('session_token')
    if session_token:
        return jsonify({"status": "pending", "message": "Verification in progress"})
    return jsonify({"status": "none", "message": "No active verification session"})

@app.route('/api/verify', methods=['POST'])
def api_verify():
    """API endpoint for verification - alternative to form submission"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    verification_token = data.get('token')
    user_code = data.get('code')
    
    if not verification_token or not user_code:
        return jsonify({"error": "Missing token or code"}), 400
    
    try:
        decrypted = decrypt_token(verification_token)
        if decrypted == user_code:
            return jsonify({"success": True, "flag": FLAG})
        else:
            return jsonify({"error": "Verification failed: code mismatch"}), 403
    except ValueError as e:
        error_msg = str(e)
        # VULNERABLE: Exposing detailed error messages creates padding oracle
        return jsonify({"error": error_msg}), 400

@app.route('/api/decrypt-test', methods=['POST'])
def decrypt_test():
    """
    Debug endpoint for testing decryption (left enabled accidentally)
    VULNERABLE: Provides direct access to the decryption oracle
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    ciphertext = data.get('ciphertext')
    if not ciphertext:
        return jsonify({"error": "Missing ciphertext"}), 400
    
    try:
        # Attempt decryption - errors reveal padding information
        result = decrypt_token(ciphertext)
        # Don't reveal actual decrypted content, just success status
        return jsonify({"status": "valid", "length": len(result)})
    except ValueError as e:
        error_msg = str(e)
        # VULNERABLE: Detailed error types enable Manger-style attack
        return jsonify({"status": "error", "error": error_msg}), 400

@app.route('/', methods=['GET', 'POST'])
def home():
    form = VerificationForm()
    if request.method == 'POST':
        user_code = request.form['verification_code']
        verification_token = request.cookies.get('verification_token')
        
        if not verification_token:
            return 'No verification token found. Please refresh the page.', 400
        
        try:
            decrypted_code = decrypt_token(verification_token)
            if decrypted_code == user_code:
                return FLAG
            else:
                return 'Verification failed! Code does not match.', 403
        except ValueError as e:
            error_msg = str(e)
            # VULNERABLE: Detailed error messages for OAEP decoding failures
            if "OAEP decoding error" in error_msg:
                return f"Decryption error: {error_msg}", 400
            elif "Invalid base64" in error_msg:
                return "Invalid token format", 400
            elif "Invalid ciphertext length" in error_msg:
                return "Invalid token size", 400
            else:
                return f"Processing error: {error_msg}", 500
    else:
        # Generate new verification code and encrypt it
        code = generate_verification_code()
        captcha_img = generate_captcha_image(code)
        encrypted_token = encrypt_token(code)
        
        response = make_response(render_template('home.html', form=form, image_data=captcha_img))
        response.set_cookie('verification_token', encrypted_token)
        return response

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

