"""
Review routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app import db
from app.models import Review, Product, Order, OrderItem
from app.utils.auth import get_current_user
from app.utils.response import success_response, error_response
from app.utils.validators import sanitize_string, validate_integer
from app.middleware.security import log_activity
import logging

reviews_bp = Blueprint('reviews', __name__)
logger = logging.getLogger(__name__)


@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    """Create product review"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", "VALIDATION_ERROR", 400)
        
        product_id = data.get('product_id')
        rating = data.get('rating')
        comment = data.get('comment')
        
        # Validate product ID
        is_valid, product_id = validate_integer(product_id, min_val=1)
        if not is_valid:
            return error_response("Invalid product ID", "VALIDATION_ERROR", 400)
        
        product = Product.query.get(product_id)
        if not product:
            return error_response("Product not found", "NOT_FOUND", 404)
        
        # Validate rating
        is_valid, rating = validate_integer(rating, min_val=1, max_val=5)
        if not is_valid:
            return error_response("Rating must be between 1 and 5", "VALIDATION_ERROR", 400)
        
        # Sanitize comment
        if comment:
            comment = sanitize_string(comment, max_length=1000)
        
        # Check if user has purchased the product
        has_purchased = db.session.query(Order).join(
            OrderItem
        ).filter(
            Order.user_id == user.id,
            OrderItem.product_id == product_id
        ).first() is not None
        
        # Check if user already reviewed
        existing_review = Review.query.filter_by(
            user_id=user.id,
            product_id=product_id
        ).first()
        
        if existing_review:
            return error_response("You have already reviewed this product", "DUPLICATE_REVIEW", 400)
        
        # Create review
        review = Review(
            user_id=user.id,
            product_id=product_id,
            rating=rating,
            comment=comment,
            is_verified_purchase=has_purchased
        )
        
        db.session.add(review)
        db.session.commit()
        
        log_activity(
            user_id=user.id,
            action='REVIEW_CREATED',
            resource='review',
            resource_id=review.id,
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        logger.info(f"Review created: {review.id} by user {user.id}")
        
        return success_response(
            data={'review_id': review.id},
            message="Review created successfully",
            status_code=201
        )
    
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        db.session.rollback()
        return error_response("Failed to create review", "REVIEW_ERROR", 500)


@reviews_bp.route('/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """Get reviews for a product"""
    try:
        is_valid, product_id = validate_integer(product_id, min_val=1)
        if not is_valid:
            return error_response("Invalid product ID", "VALIDATION_ERROR", 400)
        
        product = Product.query.get(product_id)
        if not product:
            return error_response("Product not found", "NOT_FOUND", 404)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 50:
            per_page = 10
        
        query = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc())
        total = query.count()
        reviews = query.paginate(page=page, per_page=per_page, error_out=False).items
        
        reviews_data = [
            {
                'id': r.id,
                'user_name': r.user.name,
                'rating': r.rating,
                'comment': r.comment,
                'is_verified_purchase': r.is_verified_purchase,
                'created_at': r.created_at.isoformat()
            }
            for r in reviews
        ]
        
        return success_response(
            data={
                'reviews': reviews_data,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page
                }
            },
            message="Reviews retrieved successfully"
        )
    
    except Exception as e:
        logger.error(f"Error getting reviews: {str(e)}")
        return error_response("Failed to retrieve reviews", "FETCH_ERROR", 500)
