"""
Admin panel routes with analytics, product management, user management, etc.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app import db
from app.models import (
    User, Product, ProductImage, ProductSize, Order, OrderStatus, Review,
    PromoCode, ActivityLog, UserRole
)
from app.utils.auth import get_current_user, require_admin, hash_password
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import (
    sanitize_string, validate_email, validate_password, validate_integer, 
    validate_float, validate_filename
)
from app.middleware.security import log_activity
import logging
import os
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_admin
def dashboard():
    """Get admin dashboard analytics"""
    try:
        # Total users
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        
        # Total products
        total_products = Product.query.count()
        active_products = Product.query.filter_by(is_active=True).count()
        
        # Total orders
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).count()
        completed_orders = Order.query.filter_by(status=OrderStatus.DELIVERED).count()
        
        # Revenue calculations
        total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
        
        # Revenue this month
        this_month = datetime.utcnow().replace(day=1)
        monthly_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= this_month
        ).scalar() or 0
        
        # Average order value
        avg_order_value = db.session.query(func.avg(Order.total_amount)).scalar() or 0
        
        # Recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        
        # Low stock products
        low_stock = Product.query.filter(Product.stock < 10).limit(5).all()
        
        dashboard_data = {
            'users': {
                'total': total_users,
                'active': active_users,
                'inactive': total_users - active_users
            },
            'products': {
                'total': total_products,
                'active': active_products,
                'inactive': total_products - active_products
            },
            'orders': {
                'total': total_orders,
                'pending': pending_orders,
                'completed': completed_orders,
                'avg_value': round(avg_order_value, 2)
            },
            'revenue': {
                'total': round(total_revenue, 2),
                'this_month': round(monthly_revenue, 2)
            },
            'recent_orders': [
                {
                    'id': o.id,
                    'user': o.user.name,
                    'amount': o.total_amount,
                    'status': o.status.value,
                    'date': o.created_at.isoformat()
                }
                for o in recent_orders
            ],
            'low_stock_products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'stock': p.stock
                }
                for p in low_stock
            ]
        }
        
        return success_response(data=dashboard_data, message="Dashboard retrieved successfully")
    
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        return error_response("Failed to retrieve dashboard", "FETCH_ERROR", 500)


# ==================== PRODUCT MANAGEMENT ====================

@admin_bp.route('/products', methods=['POST'])
@jwt_required()
@require_admin
def create_product():
    """Create new product"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", "VALIDATION_ERROR", 400)
        
        # Validate inputs
        name = sanitize_string(data.get('name', ''), max_length=256)
        description = sanitize_string(data.get('description', ''), max_length=5000)
        category = sanitize_string(data.get('category', ''), max_length=128)
        
        is_valid, price = validate_float(data.get('price'), min_val=0)
        if not is_valid:
            return error_response("Invalid price", "VALIDATION_ERROR", 400)
        
        is_valid, stock = validate_integer(data.get('stock'), min_val=0)
        if not is_valid:
            return error_response("Invalid stock", "VALIDATION_ERROR", 400)
        
        if not name or not category:
            return error_response("Name and category are required", "VALIDATION_ERROR", 400)
        
        # Create product
        product = Product(
            name=name,
            description=description if description else None,
            price=price,
            category=category,
            stock=stock,
            is_active=True
        )
        
        # Add sizes if provided
        sizes = data.get('sizes', [])
        for size in sizes:
            size = sanitize_string(str(size), max_length=50)
            if size:
                product_size = ProductSize(size=size)
                product.sizes.append(product_size)
        
        db.session.add(product)
        db.session.commit()
        
        log_activity(
            user_id=get_jwt_identity(),
            action='PRODUCT_CREATED',
            resource='product',
            resource_id=product.id,
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        logger.info(f"Product created: {product.id}")
        
        return success_response(
            data={'product_id': product.id},
            message="Product created successfully",
            status_code=201
        )
    
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        db.session.rollback()
        return error_response("Failed to create product", "CREATE_ERROR", 500)


@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
@require_admin
def update_product(product_id):
    """Update product"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return error_response("Product not found", "NOT_FOUND", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", "VALIDATION_ERROR", 400)
        
        # Update fields
        if 'name' in data:
            product.name = sanitize_string(data['name'], max_length=256)
        
        if 'description' in data:
            product.description = sanitize_string(data['description'], max_length=5000) or None
        
        if 'price' in data:
            is_valid, price = validate_float(data['price'], min_val=0)
            if not is_valid:
                return error_response("Invalid price", "VALIDATION_ERROR", 400)
            product.price = price
        
        if 'stock' in data:
            is_valid, stock = validate_integer(data['stock'], min_val=0)
            if not is_valid:
                return error_response("Invalid stock", "VALIDATION_ERROR", 400)
            product.stock = stock
        
        if 'category' in data:
            product.category = sanitize_string(data['category'], max_length=128)
        
        if 'is_active' in data:
            product.is_active = bool(data['is_active'])
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(
            user_id=get_jwt_identity(),
            action='PRODUCT_UPDATED',
            resource='product',
            resource_id=product.id,
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        logger.info(f"Product updated: {product.id}")
        
        return success_response(message="Product updated successfully")
    
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        db.session.rollback()
        return error_response("Failed to update product", "UPDATE_ERROR", 500)


@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
@require_admin
def delete_product(product_id):
    """Delete product"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return error_response("Product not found", "NOT_FOUND", 404)
        
        # Soft delete
        product.is_active = False
        db.session.commit()
        
        log_activity(
            user_id=get_jwt_identity(),
            action='PRODUCT_DELETED',
            resource='product',
            resource_id=product_id,
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        logger.info(f"Product deleted: {product_id}")
        
        return success_response(message="Product deleted successfully")
    
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        db.session.rollback()
        return error_response("Failed to delete product", "DELETE_ERROR", 500)


# ==================== PRODUCT IMAGE MANAGEMENT ====================

@admin_bp.route('/products/<int:product_id>/images', methods=['POST'])
@jwt_required()
@require_admin
def upload_product_image(product_id):
    """Upload product image"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return error_response("Product not found", "NOT_FOUND", 404)
        
        if 'image' not in request.files:
            return error_response("No image provided", "VALIDATION_ERROR", 400)
        
        file = request.files['image']
        
        if file.filename == '':
            return error_response("No file selected", "VALIDATION_ERROR", 400)
        
        # Validate filename
        if not validate_filename(file.filename):
            return error_response("Invalid filename", "VALIDATION_ERROR", 400)
        
        # Check file extension
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        if not file.filename.lower().rsplit('.', 1)[1].lower() in allowed_extensions:
            return error_response("Only JPEG and PNG images allowed", "INVALID_FILE_TYPE", 400)
        
        # Save image
        try:
            # Create uploads directory if not exists
            upload_dir = os.path.join(os.path.dirname(__file__), '../../uploads/products')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            filepath = os.path.join(upload_dir, filename)
            
            # Validate and save image
            img = Image.open(file)
            img.thumbnail((1024, 1024))  # Resize
            img.save(filepath, quality=85)
            
            # Create image record
            image_url = f"/uploads/products/{filename}"
            alt_text = request.form.get('alt_text', '')
            alt_text = sanitize_string(alt_text, max_length=256) if alt_text else None
            
            product_image = ProductImage(
                product_id=product_id,
                image_url=image_url,
                alt_text=alt_text,
                is_primary=request.form.get('is_primary', False) == 'true'
            )
            
            db.session.add(product_image)
            db.session.commit()
            
            log_activity(
                user_id=get_jwt_identity(),
                action='IMAGE_UPLOADED',
                resource='product_image',
                resource_id=product_image.id,
                ip_address=request.remote_addr,
                status='SUCCESS'
            )
            
            return success_response(
                data={'image_id': product_image.id, 'image_url': image_url},
                message="Image uploaded successfully",
                status_code=201
            )
        
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            return error_response("Failed to save image", "FILE_ERROR", 500)
    
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return error_response("Failed to upload image", "UPLOAD_ERROR", 500)


# ==================== PROMO CODE MANAGEMENT ====================

@admin_bp.route('/promo-codes', methods=['POST'])
@jwt_required()
@require_admin
def create_promo_code():
    """Create promo code"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", "VALIDATION_ERROR", 400)
        
        code = sanitize_string(data.get('code', ''), max_length=50).upper()
        discount_type = data.get('discount_type')  # 'percentage' or 'fixed'
        
        is_valid, discount_value = validate_float(data.get('discount_value'), min_val=0)
        if not is_valid:
            return error_response("Invalid discount value", "VALIDATION_ERROR", 400)
        
        if discount_type == 'percentage' and discount_value > 100:
            return error_response("Percentage discount cannot exceed 100", "VALIDATION_ERROR", 400)
        
        if not code or discount_type not in ['percentage', 'fixed']:
            return error_response("Invalid code or discount type", "VALIDATION_ERROR", 400)
        
        # Check duplicate code
        if PromoCode.query.filter_by(code=code).first():
            return error_response("Promo code already exists", "DUPLICATE_CODE", 409)
        
        # Parse expiration date
        expiration_date = data.get('expiration_date')
        if expiration_date:
            try:
                expiration_date = datetime.fromisoformat(expiration_date)
            except:
                return error_response("Invalid expiration date format", "VALIDATION_ERROR", 400)
        else:
            expiration_date = datetime.utcnow() + timedelta(days=30)
        
        is_valid, usage_limit = validate_integer(data.get('usage_limit'), min_val=1)
        usage_limit = usage_limit if is_valid else None
        
        is_valid, min_amount = validate_float(data.get('min_order_amount', 0), min_val=0)
        min_amount = min_amount if is_valid else 0
        
        # Create promo code
        promo = PromoCode(
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            expiration_date=expiration_date,
            usage_limit=usage_limit,
            min_order_amount=min_amount,
            is_active=True
        )
        
        db.session.add(promo)
        db.session.commit()
        
        log_activity(
            user_id=get_jwt_identity(),
            action='PROMO_CODE_CREATED',
            resource='promo_code',
            resource_id=promo.id,
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        logger.info(f"Promo code created: {code}")
        
        return success_response(
            data={'promo_code_id': promo.id, 'code': code},
            message="Promo code created successfully",
            status_code=201
        )
    
    except Exception as e:
        logger.error(f"Error creating promo code: {str(e)}")
        db.session.rollback()
        return error_response("Failed to create promo code", "CREATE_ERROR", 500)


# ==================== ACTIVITY LOGS ====================

@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
@require_admin
def get_activity_logs():
    """Get activity logs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        action = request.args.get('action', type=str)
        user_id = request.args.get('user_id', type=int)
        
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        query = ActivityLog.query
        
        if action:
            action = sanitize_string(action, 256)
            query = query.filter_by(action=action)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        total = query.count()
        logs = query.order_by(ActivityLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        ).items
        
        logs_data = [
            {
                'id': l.id,
                'user_id': l.user_id,
                'action': l.action,
                'resource': l.resource,
                'ip_address': l.ip_address,
                'status': l.status,
                'timestamp': l.timestamp.isoformat()
            }
            for l in logs
        ]
        
        return success_response(
            data={
                'logs': logs_data,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page
                }
            },
            message="Logs retrieved successfully"
        )
    
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        return error_response("Failed to retrieve logs", "FETCH_ERROR", 500)


# ==================== USER MANAGEMENT ====================

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@require_admin
def list_users():
    """List all users"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        query = User.query.order_by(User.created_at.desc())
        total = query.count()
        users = query.paginate(page=page, per_page=per_page, error_out=False).items
        
        users_data = [
            {
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'role': u.role.value,
                'is_active': u.is_active,
                'created_at': u.created_at.isoformat()
            }
            for u in users
        ]
        
        return success_response(
            data={
                'users': users_data,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page
                }
            },
            message="Users retrieved successfully"
        )
    
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return error_response("Failed to retrieve users", "FETCH_ERROR", 500)


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_admin
def update_user(user_id):
    """Update user"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", "NOT_FOUND", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", "VALIDATION_ERROR", 400)
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        if 'cash_balance' in data:
            is_valid, balance = validate_float(data['cash_balance'], min_val=0)
            if not is_valid:
                return error_response("Invalid cash balance", "VALIDATION_ERROR", 400)
            user.cash_balance = balance
        
        db.session.commit()
        
        log_activity(
            user_id=get_jwt_identity(),
            action='USER_UPDATED',
            resource='user',
            resource_id=user_id,
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        return success_response(message="User updated successfully")
    
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        db.session.rollback()
        return error_response("Failed to update user", "UPDATE_ERROR", 500)
