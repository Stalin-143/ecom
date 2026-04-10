"""
Authentication utilities including JWT and password hashing
"""
import hashlib
import hmac
import os
import secrets
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
import string
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models import User, UserRole
from app import db


PBKDF2_ITERATIONS = 600000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Hash password using salted PBKDF2-HMAC-SHA256."""
    salt = secrets.token_bytes(SALT_BYTES)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(password: str, hash_: str) -> bool:
    """Verify password against stored PBKDF2-HMAC-SHA256 hash."""
    try:
        algo, iter_str, salt_hex, hash_hex = hash_.split('$', 3)
        if algo != 'pbkdf2_sha256':
            return False

        iterations = int(iter_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def generate_tokens(user_id: int, email: str, role: UserRole):
    """Generate JWT tokens for user"""
    access_token = create_access_token(
        identity=user_id,
        additional_claims={"email": email, "role": role.value}
    )
    refresh_token = create_refresh_token(identity=user_id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }


def require_role(*roles):
    """Decorator to require specific roles"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in [role.value if isinstance(role, UserRole) else role for role in roles]:
                return jsonify({'message': 'Insufficient permissions'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_admin(fn):
    """Decorator to require admin role"""
    return require_role(UserRole.ADMIN)(fn)


def require_user(fn):
    """Decorator to require user/admin role"""
    return require_role(UserRole.USER, UserRole.ADMIN)(fn)


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


def get_current_user():
    """Get current authenticated user"""
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    return User.query.get(user_id)
