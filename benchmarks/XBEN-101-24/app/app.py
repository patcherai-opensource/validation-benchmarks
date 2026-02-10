from flask import Flask, render_template, request, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from PIL import Image, ImageDraw, ImageFont
import os
import base64
import random
import string
from base64 import b64encode
import io
from captcha.image import ImageCaptcha

# RSA-OAEP imports - using vulnerable implementation pattern
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = '6473c2599d5871cae38105a6247d56e40db3321820d619bb'

# Get flag from environment variable, fallback to placeholder for development
FLAG = os.environ.get('FLAG', '@FLAG@')

# Generate a fixed RSA key for the challenge (stored on server)
# In production this would be loaded from a secure location
RSA_KEY_BITS = 1024  # Smaller key for faster oracle attacks in CTF context
RSA_PRIVATE_KEY = None
RSA_PUBLIC_KEY = None

def init_rsa_keys():
    """Initialize RSA keys - using a fixed seed for reproducibility"""
    global RSA_PRIVATE_KEY, RSA_PUBLIC_KEY
    # Use a deterministic key for reproducibility in the challenge
    # In real vulnerability, any RSA key would be vulnerable
    random.seed(42)  # Fixed seed for key generation
    RSA_PRIVATE_KEY = RSA.generate(RSA_KEY_BITS)
    RSA_PUBLIC_KEY = RSA_PRIVATE_KEY.publickey()
    random.seed()  # Reset to random

init_rsa_keys()

def generate_captcha():
    """Generate a captcha image with partially hidden text"""
    image = ImageCaptcha(width=280, height=90)
    captcha_text = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(14))
    # Cover the last 6 characters of the captcha on the image
    captcha_text_redacted = captcha_text[:8] + "......"
    data = image.generate(captcha_text_redacted)
    base64_img = b64encode(data.getvalue()).decode('utf8')
    return captcha_text, base64_img

def encrypt_captcha_oaep(captcha_text):
    """
    Encrypt captcha using RSA-OAEP.
    This simulates the vulnerable pattern from CVE in PyCryptodome < 3.19.1
    """
    cipher = PKCS1_OAEP.new(RSA_PUBLIC_KEY, hashAlgo=SHA256)
    ciphertext = cipher.encrypt(captcha_text.encode('utf-8'))
    return base64.b64encode(ciphertext).decode('utf-8')

def vulnerable_oaep_decrypt(ciphertext_bytes):
    """
    Vulnerable OAEP decryption that leaks information through error messages.
    
    This simulates the CVE vulnerability in PyCryptodome < 3.19.1 where
    non-constant-time OAEP decoding leaks information about the decrypted
    plaintext structure.
    
    The vulnerability allows a Manger attack by distinguishing between:
    1. Ciphertexts where the first byte after RSA decryption is 0x00 (valid start)
    2. Ciphertexts where the first byte is not 0x00 (invalid)
    
    Additionally, we expose different error types for:
    - Invalid OAEP structure (missing 0x01 separator)
    - Hash mismatch in OAEP
    """
    # Get key parameters
    n = RSA_PRIVATE_KEY.n
    d = RSA_PRIVATE_KEY.d
    k = (n.bit_length() + 7) // 8  # Key length in bytes
    
    # Check ciphertext length
    if len(ciphertext_bytes) != k:
        raise ValueError("Decryption error: Invalid ciphertext length")
    
    # RSA decryption: m = c^d mod n
    c_int = int.from_bytes(ciphertext_bytes, 'big')
    m_int = pow(c_int, d, n)
    
    # Convert to bytes with proper padding
    decrypted = m_int.to_bytes(k, 'big')
    
    # VULNERABLE: Non-constant-time OAEP unpadding
    # This is the core vulnerability - we leak information about the structure
    
    # Hash length for SHA256
    hLen = 32
    
    # OAEP structure: Y || maskedSeed || maskedDB
    # Y = 1 byte (must be 0x00)
    # maskedSeed = hLen bytes
    # maskedDB = k - hLen - 1 bytes
    
    # Check that first byte is 0x00 (OAEP requirement)
    # VULNERABLE: This check leaks whether the first byte is 0x00
    # This is the key oracle for Manger's attack
    if decrypted[0] != 0x00:
        raise ValueError("Decryption error: Invalid OAEP encoding (first byte)")
    
    # Split into maskedSeed and maskedDB
    maskedSeed = decrypted[1:1+hLen]
    maskedDB = decrypted[1+hLen:]
    
    # MGF1 for mask generation
    def mgf1(seed, length, hash_func=hashlib.sha256):
        output = b''
        counter = 0
        while len(output) < length:
            C = counter.to_bytes(4, 'big')
            output += hash_func(seed + C).digest()
            counter += 1
        return output[:length]
    
    # OAEP unmasking (correct order per PKCS#1 v2.1):
    # Step 1: seedMask = MGF(maskedDB, hLen)
    seedMask = mgf1(maskedDB, hLen)
    # Step 2: seed = maskedSeed XOR seedMask
    seed = bytes(a ^ b for a, b in zip(maskedSeed, seedMask))
    # Step 3: dbMask = MGF(seed, k - hLen - 1)
    dbMask = mgf1(seed, k - hLen - 1)
    # Step 4: DB = maskedDB XOR dbMask
    DB = bytes(a ^ b for a, b in zip(maskedDB, dbMask))
    
    # DB = lHash || PS || 0x01 || M
    # Extract lHash from DB
    lHash_received = DB[:hLen]
    
    # Expected lHash (empty label)
    lHash_expected = hashlib.sha256(b'').digest()
    
    # VULNERABLE: Non-constant-time hash comparison
    # This leaks whether the hash matches
    if lHash_received != lHash_expected:
        raise ValueError("Decryption error: OAEP hash mismatch")
    
    # Find the 0x01 separator in PS || 0x01 || M
    # VULNERABLE: This search is not constant-time and leaks the position
    padding_section = DB[hLen:]
    separator_pos = -1
    
    for i, byte in enumerate(padding_section):
        if byte == 0x01:
            separator_pos = i
            break
        elif byte != 0x00:
            # Invalid padding byte before separator
            raise ValueError("Decryption error: Invalid OAEP padding structure")
    
    if separator_pos == -1:
        raise ValueError("Decryption error: OAEP separator not found")
    
    # Extract message
    message = padding_section[separator_pos + 1:]
    return message

def decrypt_captcha_oaep(cookie_value):
    """
    Decrypt the captcha cookie using vulnerable OAEP decryption.
    Returns the plaintext captcha string.
    """
    try:
        ciphertext = base64.b64decode(cookie_value)
        plaintext = vulnerable_oaep_decrypt(ciphertext)
        return plaintext
    except Exception as e:
        # Re-raise with the same error message to preserve the oracle
        raise e

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
            return 'Missing captcha cookie', 400
            
        try:
            decrypted_captcha = decrypt_captcha_oaep(cookie_captcha)
            if decrypted_captcha.decode('UTF-8') == user_captcha:
                return FLAG
            else:
                return 'Invalid CAPTCHA!', 403
        except ValueError as e:
            error_msg = str(e)
            # VULNERABLE: Different error messages create an oracle
            if "first byte" in error_msg:
                return "Decryption error: OAEP first byte invalid", 400
            elif "hash mismatch" in error_msg:
                return "Decryption error: OAEP hash verification failed", 400
            elif "padding structure" in error_msg:
                return "Decryption error: OAEP padding invalid", 400
            elif "separator" in error_msg:
                return "Decryption error: OAEP structure invalid", 400
            elif "length" in error_msg:
                return "Decryption error: Invalid ciphertext length", 400
            else:
                return f"Decryption error: {error_msg}", 400
        except Exception as e:
            return f"Decryption error: Unknown error", 400
                
    else:
        captcha_text, base64_img = generate_captcha()
        encrypted_captcha = encrypt_captcha_oaep(captcha_text)

        response = make_response(render_template('home.html', form=form, image_data=base64_img))
        response.set_cookie('captcha', encrypted_captcha)
        return response

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK', 200

@app.route('/pubkey')
def pubkey():
    """
    Expose the RSA public key for encryption.
    This is needed for the Manger attack - attacker needs n and e.
    """
    return {
        'n': hex(RSA_PUBLIC_KEY.n),
        'e': hex(RSA_PUBLIC_KEY.e),
        'key_size': RSA_KEY_BITS
    }

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

