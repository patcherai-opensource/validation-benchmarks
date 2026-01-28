
class Workspace():
    """Represents a user workspace in the collaboration platform"""
    def __init__(self, name='Default Workspace', description='A workspace for collaboration'):
        self.name = name
        self.description = description
        self.created_at = None
        self.status = 'active'

class UrlObj():
    """Legacy class - kept for backward compatibility"""
    def __init__(self, name='Url', url='http://example.com'):
        self.name = name
        self.url = url
