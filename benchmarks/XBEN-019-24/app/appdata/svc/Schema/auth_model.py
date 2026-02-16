"""
VaultKeeper - Authentication Model
Database operations for user authentication
"""

class AuthModel:
    def __init__(self, db):
        self.db = db

    def get_user_by_login(self, login):
        """Find user by login name"""
        query = "SELECT * FROM users WHERE login = %s AND disabled = 0"
        result = self.db.select(query, (login,))
        return result[0] if result else None

    def verify_password(self, stored_hash, password):
        """Verify password against stored hash"""
        import hashlib
        computed = hashlib.sha256(password.encode()).hexdigest()
        return computed == stored_hash

    def update_last_login(self, user_id):
        """Update last login timestamp"""
        query = "UPDATE users SET last_login = NOW() WHERE id = %s"
        self.db.execute(query, (user_id,))

    def get_api_key(self, key_value):
        """Validate API key"""
        query = "SELECT * FROM api_keys WHERE value = %s AND enabled = 1"
        result = self.db.select(query, (key_value,))
        return result[0] if result else None
