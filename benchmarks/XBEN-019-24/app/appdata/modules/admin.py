"""
VaultKeeper - Admin Module
Administrative settings and dashboard
"""

def render_admin_page(session_data, settings):
    """Render the admin dashboard"""
    if not session_data.get('is_admin', False):
        return {'error': True, 'message': 'Admin access required'}
    return {'error': False, 'template': 'admin'}

def render_options_page(session_data, settings):
    """Render the options/settings page"""
    if not session_data.get('is_admin', False):
        return {'error': True, 'message': 'Admin access required'}
    return {'error': False, 'template': 'options'}
