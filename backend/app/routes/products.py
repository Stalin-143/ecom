"""
Product routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app import db, limiter
from app.models import Product, ProductImage, ProductSize, Review
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import sanitize_string, validate_integer
import logging

products_bp = Blueprint('products', __name__)
logger = logging.getLogger(__name__)


@products_bp.route('', methods=['GET'])
@limiter.limit("30 per minute")
def list_products():
    """List products with pagination and filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        category = request.args.get('category', type=str)
        search = request.args.get('search', type=str)
        sort_by = request.args.get('sort_by', 'created_at', type=str)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 12
        
        # Build query
        query = Product.query.filter_by(is_active=True)
        
        # Apply category filter
        if category:
            category = sanitize_string(category, 128)
            query = query.filter_by(category=category)
        
        # Apply search filter
        if search:
            search = sanitize_string(search, 128)
            query = query.filter(
                db.or_(
                    Product.name.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%')
                )
            )
        
        # Get distinct categories for filter options
        categories = db.session.query(func.distinct(Product.category)).all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        # Apply sorting
        if sort_by == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Product.price.desc())
        else:
            query = query.order_by(Product.created_at.desc())
        
        # Paginate
        total = query.count()
        products = query.paginate(page=page, per_page=per_page, error_out=False).items
        
        # Format response
        products_data = [
            {
                'id': p.id,
                'name': p.name,
                'description': p.description[:200] if p.description else None,
                'price': p.price,
                'category': p.category,
                'stock': p.stock,
                'average_rating': db.session.query(func.avg(Review.rating)).filter_by(product_id=p.id).scalar() or 0,
                'images': [{'id': img.id, 'url': img.image_url, 'is_primary': img.is_primary} for img in p.images]
            }
            for p in products
        ]
        
        return success_response(
            data={
                'products': products_data,
                'categories': categories,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page
                }
            },
            message="Products retrieved successfully"
        )
    
    except Exception as e:
        logger.error(f"Error listing products: {str(e)}")
        return error_response("Failed to retrieve products", "FETCH_ERROR", 500)


@products_bp.route('/<int:product_id>', methods=['GET'])
@limiter.limit("60 per minute")
def get_product(product_id):
    """Get product details"""
    try:
        product = Product.query.get(product_id)
        
        if not product or not product.is_active:
            return error_response("Product not found", "NOT_FOUND", 404)
        
        # Get reviews
        reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'category': product.category,
            'stock': product.stock,
            'created_at': product.created_at.isoformat(),
            'images': [
                {
                    'id': img.id,
                    'url': img.image_url,
                    'alt_text': img.alt_text,
                    'is_primary': img.is_primary
                }
                for img in product.images
            ],
            'sizes': [{'id': s.id, 'size': s.size} for s in product.sizes],
            'average_rating': db.session.query(func.avg(Review.rating)).filter_by(product_id=product_id).scalar() or 0,
            'review_count': len(reviews),
            'reviews': [
                {
                    'id': r.id,
                    'user_name': r.user.name,
                    'rating': r.rating,
                    'comment': r.comment,
                    'created_at': r.created_at.isoformat()
                }
                for r in reviews[:5]  # Latest 5 reviews
            ]
        }
        
        return success_response(data=product_data, message="Product retrieved successfully")
    
    except Exception as e:
        logger.error(f"Error getting product: {str(e)}")
        return error_response("Failed to retrieve product", "FETCH_ERROR", 500)


@products_bp.route('/categories', methods=['GET'])
@limiter.limit("30 per minute")
def get_categories():
    """Get all categories"""
    try:
        categories = db.session.query(
            func.distinct(Product.category)
        ).filter(Product.is_active == True).all()
        
        categories = [cat[0] for cat in categories if cat[0]]
        
        return success_response(
            data={'categories': sorted(categories)},
            message="Categories retrieved successfully"
        )
    
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return error_response("Failed to retrieve categories", "FETCH_ERROR", 500)
