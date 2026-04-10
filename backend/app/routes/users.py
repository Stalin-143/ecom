"""
User profile routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app import db
from app.models import User
from app.utils.auth import get_current_user, hash_password, verify_password
from app.utils.response import success_response, error_response
from app.utils.validators import validate_email, validate_password, validate_phone, sanitize_string
from app.middleware.security import log_activity
import logging

users_bp = Blueprint('users', __name__)
logger = logging.getLogger(__name__)


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user = get_current_user()
        
        return success_response(
            data={
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'address': user.address,
                'phone': user.phone,
                'cash_balance': user.cash_balance,
                'role': user.role.value,
                'created_at': user.created_at.isoformat()
            },
            message="Profile retrieved successfully"
        )
    
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return error_response("Failed to retrieve profile", "FETCH_ERROR", 500)


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", "VALIDATION_ERROR", 400)
        
        # Update name
        if 'name' in data:
            name = sanitize_string(data['name'], max_length=128)
            if not name:
                return error_response("Invalid name", "VALIDATION_ERROR", 400)
            user.name = name
        
        # Update address
        if 'address' in data:
            address = sanitize_string(data['address'], max_length=512)
            user.address = address if address else None
        
        # Update phone
        if 'phone' in data:
            phone = data['phone']
            if phone and not validate_phone(phone):
                return error_response("Invalid phone number", "VALIDATION_ERROR", 400)
            user.phone = phone if phone else None
        
        db.session.commit()
        
        log_activity(
            user_id=user.id,
            action='PROFILE_UPDATED',
            resource='user',
            resource_id=user.id,
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        logger.info(f"User {user.id} updated profile")
        
        return success_response(
            data={
                'id': user.id,
                'name': user.name,
                'address': user.address,
                'phone': user.phone
            },
            message="Profile updated successfully"
        )
    
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        db.session.rollback()
        return error_response("Failed to update profile", "UPDATE_ERROR", 500)


@users_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", "VALIDATION_ERROR", 400)
        
        old_password = data.get('old_password', '').strip()
        new_password = data.get('new_password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            log_activity(
                user_id=user.id,
                action='PASSWORD_CHANGE_FAILED',
                resource='user',
                resource_id=user.id,
                ip_address=request.remote_addr,
                status='FAILED',
                details={'reason': 'Invalid old password'}
            )
            return error_response("Invalid current password", "INVALID_PASSWORD", 401)
        
        # Check if new passwords match
        if new_password != confirm_password:
            return error_response("New passwords do not match", "VALIDATION_ERROR", 400)
        
        # Validate new password
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            return error_response(msg, "WEAK_PASSWORD", 400)
        
        # Prevent reusing same password
        if verify_password(new_password, user.password_hash):
            return error_response("New password cannot be same as old password", "VALIDATION_ERROR", 400)
        
        # Update password
        user.password_hash = hash_password(new_password)
        db.session.commit()
        
        log_activity(
            user_id=user.id,
            action='PASSWORD_CHANGED',
            resource='user',
            resource_id=user.id,
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        logger.info(f"User {user.id} changed password")
        
        return success_response(message="Password changed successfully")
    
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        db.session.rollback()
        return error_response("Failed to change password", "UPDATE_ERROR", 500)
