"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, UserRole, ActivityLog
from app.utils.auth import (
    hash_password, verify_password, generate_tokens, get_current_user
)
from app.utils.validators import (
    validate_email, validate_password, sanitize_string, is_sql_injection_attempt
)
from app.utils.response import success_response, error_response
from app.middleware.security import log_activity
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return error_response("No data provided", "VALIDATION_ERROR", 400)
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        
        # Validate email
        is_valid, email_result = validate_email(email)
        if not is_valid:
            return error_response(f"Invalid email: {email_result}", "INVALID_EMAIL", 400)
        
        # Check if user exists
        if User.query.filter_by(email=email_result).first():
            return error_response("Email already registered", "EMAIL_EXISTS", 409)
        
        # Validate password
        is_valid, msg = validate_password(password)
        if not is_valid:
            return error_response(msg, "WEAK_PASSWORD", 400)
        
        # Sanitize name
        name = sanitize_string(name, max_length=128)
        if not name:
            return error_response("Invalid name", "INVALID_NAME", 400)
        
        # Create user
        user = User(
            email=email_result,
            name=name,
            password_hash=hash_password(password),
            role=UserRole.USER,
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log activity
        log_activity(
            user_id=user.id,
            action='USER_REGISTERED',
            resource='user',
            resource_id=user.id,
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        logger.info(f"New user registered: {email_result}")
        
        return success_response(
            data={'user_id': user.id, 'email': user.email},
            message="User registered successfully",
            status_code=201
        )
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return error_response("Registration failed", "REGISTER_ERROR", 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", "VALIDATION_ERROR", 400)
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not verify_password(password, user.password_hash):
            log_activity(
                action='LOGIN_FAILED',
                resource='auth',
                ip_address=request.remote_addr,
                status='FAILED',
                details={'reason': 'Invalid credentials'}
            )
            return error_response("Invalid email or password", "INVALID_CREDENTIALS", 401)
        
        if not user.is_active:
            return error_response("User account is disabled", "ACCOUNT_DISABLED", 403)
        
        # Generate tokens
        tokens = generate_tokens(user.id, user.email, user.role)
        
        # Log activity
        log_activity(
            user_id=user.id,
            action='USER_LOGIN',
            resource='auth',
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        logger.info(f"User login successful: {email}")
        
        return success_response(
            data={
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role.value,
                **tokens
            },
            message="Login successful"
        )
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return error_response("Login failed", "LOGIN_ERROR", 500)


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_access_token():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return error_response("User not found or disabled", "USER_NOT_FOUND", 401)
        
        tokens = generate_tokens(user.id, user.email, user.role)
        
        return success_response(
            data=tokens,
            message="Token refreshed successfully"
        )
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return error_response("Token refresh failed", "REFRESH_ERROR", 500)


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    """Get current user information"""
    try:
        user = get_current_user()
        
        if not user:
            return error_response("User not found", "USER_NOT_FOUND", 404)
        
        return success_response(
            data={
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role.value,
                'address': user.address,
                'phone': user.phone,
                'cash_balance': user.cash_balance,
                'created_at': user.created_at.isoformat()
            },
            message="User information retrieved"
        )
    
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        return error_response("Failed to retrieve user info", "FETCH_ERROR", 500)


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    try:
        user_id = get_jwt_identity()
        
        log_activity(
            user_id=user_id,
            action='USER_LOGOUT',
            resource='auth',
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        return success_response(message="Logout successful")
    
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return error_response("Logout failed", "LOGOUT_ERROR", 500)
