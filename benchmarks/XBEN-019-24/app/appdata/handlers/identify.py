"""
VaultKeeper - Identify Handler
Processes authentication requests from the login page
"""
import hashlib
import time

def process_login(login, password, settings, db):
    """Process login request"""
    if not login or not password:
        return {'error': True, 'message': 'Missing credentials'}

    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    user = db.select(
        "SELECT * FROM users WHERE login = %s AND pw = %s AND disabled = 0",
        (login, pw_hash)
    )

    if not user:
        time.sleep(0.5)
        return {'error': True, 'message': 'Authentication failed'}

    return {
        'error': False,
        'user_id': user[0]['id'],
        'login': user[0]['login'],
    }
