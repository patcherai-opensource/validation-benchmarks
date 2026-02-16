"""
VaultKeeper - Users Module
User management page logic
"""

def render_users_page(session_data, settings):
    """Render the user management interface"""
    if not session_data.get('is_admin', False):
        return {'error': True, 'message': 'Admin access required'}
    return {'error': False, 'template': 'users'}

def render_roles_page(session_data, settings):
    """Render the roles management interface"""
    if not session_data.get('is_admin', False):
        return {'error': True, 'message': 'Admin access required'}
    return {'error': False, 'template': 'roles'}
