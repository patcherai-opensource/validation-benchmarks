"""
VaultKeeper - User Model
Database operations for user management
"""

class UserModel:
    def __init__(self, db):
        self.db = db

    def get_user_by_id(self, user_id):
        """Get user details by ID"""
        query = "SELECT id, login, name, email, role_id, disabled FROM users WHERE id = %s"
        result = self.db.select(query, (user_id,))
        return result[0] if result else None

    def get_all_users(self):
        """Get all users (admin function)"""
        query = "SELECT id, login, name, email, role_id, disabled, last_login FROM users"
        return self.db.select(query)
