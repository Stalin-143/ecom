"""
API response utilities for consistent response format
"""
from flask import jsonify
from typing import Any, Dict, Optional


def success_response(
    data: Any = None,
    message: str = "Request successful",
    status_code: int = 200
) -> tuple:
    """Return standardized success response"""
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code


def error_response(
    message: str,
    error_code: str = "GENERAL_ERROR",
    status_code: int = 400,
    details: Optional[Dict] = None
) -> tuple:
    """Return standardized error response"""
    response = {
        'success': False,
        'message': message,
        'error_code': error_code,
    }
    if details:
        response['details'] = details
    
    return jsonify(response), status_code


def paginated_response(
    items: list,
    total: int,
    page: int,
    per_page: int,
    message: str = "Records retrieved successfully"
) -> tuple:
    """Return paginated response"""
    response = {
        'success': True,
        'message': message,
        'data': items,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    }
    return jsonify(response), 200
