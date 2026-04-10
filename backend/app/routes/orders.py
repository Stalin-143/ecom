"""
Order routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Order, OrderItem, Product, PromoCode, User, OrderStatus
from app.utils.auth import get_current_user
from app.utils.response import success_response, error_response
from app.utils.validators import validate_integer, validate_float, sanitize_string
from app.middleware.security import log_activity
from datetime import datetime
import logging

orders_bp = Blueprint('orders', __name__)
logger = logging.getLogger(__name__)


@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """Create new order"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data or 'items' not in data:
            return error_response("Invalid order data", "VALIDATION_ERROR", 400)
        
        items = data.get('items', [])
        if not items:
            return error_response("Order must contain items", "VALIDATION_ERROR", 400)
        
        promo_code_id = data.get('promo_code_id')
        shipping_address = data.get('shipping_address', user.address)
        payment_method = data.get('payment_method', 'card')
        
        if not shipping_address:
            return error_response("Shipping address required", "VALIDATION_ERROR", 400)
        
        shipping_address = sanitize_string(shipping_address, max_length=512)
        
        # Calculate total
        total_amount = 0
        order_items_to_add = []
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity')
            
            is_valid, product_id = validate_integer(product_id, min_val=1)
            if not is_valid:
                return error_response("Invalid product ID", "VALIDATION_ERROR", 400)
            
            is_valid, quantity = validate_integer(quantity, min_val=1, max_val=1000)
            if not is_valid:
                return error_response("Invalid quantity", "VALIDATION_ERROR", 400)
            
            product = Product.query.get(product_id)
            if not product:
                return error_response(f"Product {product_id} not found", "NOT_FOUND", 404)
            
            if product.stock < quantity:
                return error_response(f"Insufficient stock for {product.name}", "OUT_OF_STOCK", 400)
            
            item_total = product.price * quantity
            total_amount += item_total
            
            order_items_to_add.append({
                'product': product,
                'quantity': quantity,
                'price': product.price
            })
        
        # Apply promo code if provided
        discount = 0
        if promo_code_id:
            promo = PromoCode.query.get(promo_code_id)
            
            if not promo:
                return error_response("Promo code not found", "NOT_FOUND", 404)
            
            if not promo.is_active or promo.expiration_date < datetime.utcnow():
                return error_response("Promo code expired", "INVALID_CODE", 400)
            
            if promo.usage_limit and promo.usage_count >= promo.usage_limit:
                return error_response("Promo code usage limit exceeded", "INVALID_CODE", 400)
            
            if promo.min_order_amount and total_amount < promo.min_order_amount:
                return error_response(
                    f"Minimum order amount {promo.min_order_amount} required",
                    "INVALID_CODE", 400
                )
            
            if promo.discount_type.value == 'percentage':
                discount = total_amount * (promo.discount_value / 100)
            else:
                discount = promo.discount_value
            
            promo.usage_count += 1
        
        final_amount = max(total_amount - discount, 0)
        
        # Create order
        order = Order(
            user_id=user.id,
            total_amount=final_amount,
            shipping_address=shipping_address,
            payment_method=payment_method,
            promo_code_id=promo_code_id if promo_code_id else None,
            status=OrderStatus.PENDING
        )
        
        db.session.add(order)
        db.session.flush()
        
        # Add order items
        for item_data in order_items_to_add:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)
            
            # Update product stock
            item_data['product'].stock -= item_data['quantity']
        
        db.session.commit()
        
        # Log activity
        log_activity(
            user_id=user.id,
            action='ORDER_CREATED',
            resource='order',
            resource_id=order.id,
            ip_address=request.remote_addr,
            status='SUCCESS'
        )
        
        logger.info(f"Order created: {order.id} by user {user.id}")
        
        return success_response(
            data={
                'order_id': order.id,
                'total_amount': order.total_amount,
                'status': order.status.value,
                'discount': discount,
                'original_amount': total_amount
            },
            message="Order created successfully",
            status_code=201
        )
    
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        db.session.rollback()
        return error_response("Failed to create order", "ORDER_ERROR", 500)


@orders_bp.route('', methods=['GET'])
@jwt_required()
def list_user_orders():
    """List user's orders"""
    try:
        user = get_current_user()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 50:
            per_page = 10
        
        query = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc())
        total = query.count()
        orders = query.paginate(page=page, per_page=per_page, error_out=False).items
        
        orders_data = [
            {
                'id': o.id,
                'status': o.status.value,
                'total_amount': o.total_amount,
                'created_at': o.created_at.isoformat(),
                'updated_at': o.updated_at.isoformat(),
                'items_count': len(o.order_items)
            }
            for o in orders
        ]
        
        return success_response(
            data={
                'orders': orders_data,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page
                }
            },
            message="Orders retrieved successfully"
        )
    
    except Exception as e:
        logger.error(f"Error listing orders: {str(e)}")
        return error_response("Failed to retrieve orders", "FETCH_ERROR", 500)


@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get order details"""
    try:
        user = get_current_user()
        order = Order.query.get(order_id)
        
        if not order or order.user_id != user.id:
            return error_response("Order not found", "NOT_FOUND", 404)
        
        order_data = {
            'id': order.id,
            'status': order.status.value,
            'total_amount': order.total_amount,
            'shipping_address': order.shipping_address,
            'payment_method': order.payment_method,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat(),
            'items': [
                {
                    'product_id': oi.product_id,
                    'product_name': oi.product.name,
                    'quantity': oi.quantity,
                    'price': oi.price
                }
                for oi in order.order_items
            ]
        }
        
        return success_response(data=order_data, message="Order retrieved successfully")
    
    except Exception as e:
        logger.error(f"Error getting order: {str(e)}")
        return error_response("Failed to retrieve order", "FETCH_ERROR", 500)
