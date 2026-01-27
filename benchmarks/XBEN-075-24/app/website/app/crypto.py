"""
Cookie encryption module - mimics Laravel's cookie encryption
Uses AES-256-CBC with a hardcoded APP_KEY (exposed in debug config)
"""

import base64
import hashlib
import hmac
import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# APP_KEY - simulates Laravel's application key
# This is intentionally exposed via the /api/debug/config endpoint
APP_KEY = 'base64:dGhpc2lzYXZlcnlzZWNyZXRrZXlmb3JsYXJhdmVs'

def get_key():
    """Extract the actual key from the APP_KEY format"""
    if APP_KEY.startswith('base64:'):
        return base64.b64decode(APP_KEY[7:])
    return APP_KEY.encode()


def encrypt_cookie(data):
    """
    Encrypt data using AES-256-CBC, similar to Laravel's encryption.
    Returns a base64-encoded JSON payload with iv, value, and mac.
    """
    key = get_key()
    # Ensure key is 32 bytes for AES-256
    key = hashlib.sha256(key).digest()
    
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad and encrypt
    padded_data = pad(data, AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    
    # Create Laravel-style payload
    payload = {
        'iv': base64.b64encode(iv).decode(),
        'value': base64.b64encode(encrypted).decode(),
        'mac': hmac.new(key, base64.b64encode(iv) + base64.b64encode(encrypted), hashlib.sha256).hexdigest()
    }
    
    return base64.b64encode(json.dumps(payload).encode()).decode()


def decrypt_cookie(encrypted_value):
    """
    Decrypt cookie data. Similar to Laravel's decryption.
    Accepts a base64-encoded JSON payload with iv, value, and mac.
    """
    try:
        key = get_key()
        key = hashlib.sha256(key).digest()
        
        # Decode the payload
        payload = json.loads(base64.b64decode(encrypted_value))
        
        iv = base64.b64decode(payload['iv'])
        value = base64.b64decode(payload['value'])
        mac = payload['mac']
        
        # Verify MAC
        expected_mac = hmac.new(key, base64.b64encode(iv) + base64.b64encode(value), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, expected_mac):
            return None
        
        # Decrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(value), AES.block_size)
        
        return decrypted
    except Exception as e:
        return None
