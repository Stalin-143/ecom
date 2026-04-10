"""
CSRF Protection middleware
"""
from flask import request, session
from functools import wraps
from app.utils.auth import generate_secure_token
import logging

logger = logging.getLogger(__name__)

CSRF_TOKEN_LENGTH = 32
CSRF_SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


def csrf_protect(fn):
    """
    Decorator to protect against CSRF attacks
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method in CSRF_SAFE_METHODS:
            return fn(*args, **kwargs)
        
        # Check CSRF token in headers or form data
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        session_token = session.get('csrf_token')
        
        if not token or not session_token or token != session_token:
            logger.warning(f"CSRF token mismatch from {request.remote_addr}")
            return {'message': 'CSRF token invalid or missing'}, 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def generate_csrf_token():
    """Generate CSRF token for session"""
    token = generate_secure_token(CSRF_TOKEN_LENGTH)
    session['csrf_token'] = token
    return token


def get_csrf_token():
    """Get CSRF token from session or generate new one"""
    token = session.get('csrf_token')
    if not token:
        token = generate_csrf_token()
    return token
