"""
Models for the ArtisanCMS application
These classes are serialized and stored in cookies
"""

import os
from datetime import datetime


class UserPreferences:
    """User preferences stored in session cookie"""
    def __init__(self, user_id='anonymous', theme='light', notifications=True, display_name=''):
        self.user_id = user_id
        self.theme = theme
        self.notifications = notifications
        self.display_name = display_name
        self.created_at = datetime.now().isoformat()
    
    def __repr__(self):
        return f"<UserPreferences user_id={self.user_id} theme={self.theme}>"


class Notification:
    """Notification object stored in xsrf_token cookie"""
    def __init__(self, message='', created_at=None):
        self.message = message
        self.created_at = created_at or datetime.now().isoformat()
        self.read = False
    
    def __repr__(self):
        return f"<Notification message={self.message[:20]}...>"


class FlagReader:
    """
    Gadget class that reads environment variables when unpickled.
    This is the target for the deserialization exploit.
    """
    def __init__(self, env_var='FLAG'):
        self.env_var = env_var
    
    def __reduce__(self):
        # This method is called during pickling
        # When unpickled, it will execute os.getenv with the env_var
        return (os.getenv, (self.env_var,))
