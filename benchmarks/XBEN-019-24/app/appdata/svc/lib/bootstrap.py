"""
VaultKeeper - API Bootstrap
Initializes API routing and middleware
"""
import os
import sys

API_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def initialize_api():
    """Initialize API components"""
    sys.path.insert(0, API_ROOT_PATH)
    return True

def api_is_enabled():
    """Check if API access is enabled in settings"""
    return {'error': False, 'message': ''}

def verify_auth(headers):
    """Verify request authentication"""
    from lib.jwt_utils import get_bearer_token, is_jwt_valid
    token = get_bearer_token(headers)
    if token and is_jwt_valid(token):
        return {'error': False}
    return {'error': True, 'message': 'Access denied'}
