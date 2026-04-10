# E-Commerce Platform - Backend Setup

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Initialize Database
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

### 4. Run Development Server
```bash
python run.py
```

The API will be available at `http://localhost:5000/api/v1/`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - User logout

### Products
- `GET /api/v1/products` - List products (with pagination, filtering, search)
- `GET /api/v1/products/<id>` - Get product details
- `GET /api/v1/products/categories` - Get all categories

### Orders
- `POST /api/v1/orders` - Create order
- `GET /api/v1/orders` - List user orders
- `GET /api/v1/orders/<id>` - Get order details

### Users
- `GET /api/v1/users/profile` - Get profile
- `PUT /api/v1/users/profile` - Update profile
- `POST /api/v1/users/change-password` - Change password

### Reviews
- `POST /api/v1/reviews` - Create review
- `GET /api/v1/reviews/<product_id>` - Get product reviews

### Admin
- `GET /api/v1/admin/dashboard` - Dashboard analytics
- `POST /api/v1/admin/products` - Create product
- `PUT /api/v1/admin/products/<id>` - Update product
- `DELETE /api/v1/admin/products/<id>` - Delete product
- `POST /api/v1/admin/products/<id>/images` - Upload product image
- `POST /api/v1/admin/promo-codes` - Create promo code
- `GET /api/v1/admin/logs` - Get activity logs
- `GET /api/v1/admin/users` - List users
- `PUT /api/v1/admin/users/<id>` - Update user

## Security Features

✓ Input validation and sanitization
✓ SQL Injection prevention
✓ XSS protection
✓ CSRF protection
✓ Password hashing with bcrypt
✓ JWT authentication
✓ Role-based access control (RBAC)
✓ Rate limiting
✓ Security headers (CSP, HSTS, X-Frame-Options, etc.)
✓ Activity logging
✓ File upload validation

## Database Schema

See `app/models/__init__.py` for complete schema definition.

Main tables:
- users
- products
- product_images
- product_sizes
- reviews
- orders
- order_items
- promo_codes
- logs
