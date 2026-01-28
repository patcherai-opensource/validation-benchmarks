
class SessionEntry():
    """Represents a session key-value entry"""
    def __init__(self, key='session_key', value='session_value'):
        self.key = key
        self.value = value

class UserProfile():
    """User profile for authentication"""
    def __init__(self, username='user', role='guest'):
        self.username = username
        self.role = role
