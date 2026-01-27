
class SessionData():
    """Represents a user session entry"""
    def __init__(self, session_id='', session_name='Default Session', ip_address='127.0.0.1'):
        self.session_id = session_id
        self.session_name = session_name
        self.ip_address = ip_address
        self.created_at = None
        
    def __repr__(self):
        return f'<Session {self.session_id}: {self.session_name}>'
