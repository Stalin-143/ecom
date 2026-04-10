# E-Commerce API Documentation

## Overview

RESTful API for the e-commerce platform with comprehensive endpoints for user management, product catalog, orders, and admin operations.

**Base URL:** `http://localhost:5000/api/v1`  
**API Version:** 1.0  
**Authentication:** JWT Bearer Token

## Authentication

### Headers Required
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Refresh
Access tokens expire after 1 hour. Use refresh token to get new access token:

```
POST /auth/refresh
Headers:
  Authorization: Bearer <refresh_token>
```

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Request successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": { ... }
}
```

## Endpoints

### 1. Authentication

#### Register
```
POST /auth/register

Request:
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response (201):
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": 1,
    "email": "john@example.com"
  }
}
```

#### Login
```
POST /auth/login

Request:
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user_id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "role": "user",
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "Bearer"
  }
}
```

#### Get Current User
```
GET /auth/me
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "address": "123 Main St",
    "phone": "+1234567890",
    "cash_balance": 100.00,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 2. Products

#### List Products
```
GET /products?page=1&per_page=12&category=Clothing&search=shirt&sort_by=price_asc

Parameters:
  page (int, default: 1)
  per_page (int, default: 12, max: 100)
  category (string, optional)
  search (string, optional)
  sort_by (string, options: created_at, price_asc, price_desc)

Response (200):
{
  "success": true,
  "data": {
    "products": [
      {
        "id": 1,
        "name": "T-Shirt",
        "description": "Comfortable cotton t-shirt",
        "price": 29.99,
        "category": "Clothing",
        "stock": 50,
        "average_rating": 4.5,
        "images": [
          {
            "id": 1,
            "url": "/uploads/products/img1.jpg",
            "is_primary": true
          }
        ]
      }
    ],
    "categories": ["Clothing", "Grocery", "Dress"],
    "pagination": {
      "total": 100,
      "page": 1,
      "per_page": 12,
      "total_pages": 9
    }
  }
}
```

#### Get Product Details
```
GET /products/{id}

Response (200):
{
  "success": true,
  "data": {
    "id": 1,
    "name": "T-Shirt",
    "description": "Detailed description",
    "price": 29.99,
    "category": "Clothing",
    "stock": 50,
    "images": [...],
    "sizes": ["S", "M", "L", "XL"],
    "average_rating": 4.5,
    "review_count": 12,
    "reviews": [
      {
        "id": 1,
        "user_name": "John",
        "rating": 5,
        "comment": "Great product!",
        "created_at": "2024-01-01T00:00:00"
      }
    ]
  }
}
```

#### Get Categories
```
GET /products/categories

Response (200):
{
  "success": true,
  "data": {
    "categories": ["Clothing", "Dress", "Grocery"]
  }
}
```

### 3. Orders

#### Create Order
```
POST /orders
Authorization: Bearer <token>

Request:
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ],
  "shipping_address": "123 Main St, City, State 12345",
  "payment_method": "card",
  "promo_code_id": 5
}

Response (201):
{
  "success": true,
  "message": "Order created successfully",
  "data": {
    "order_id": 1,
    "total_amount": 89.99,
    "status": "pending",
    "discount": 10.00,
    "original_amount": 99.99
  }
}
```

#### List User Orders
```
GET /orders?page=1&per_page=10
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "orders": [
      {
        "id": 1,
        "status": "pending",
        "total_amount": 89.99,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "items_count": 3
      }
    ],
    "pagination": {...}
  }
}
```

#### Get Order Details
```
GET /orders/{id}
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "id": 1,
    "status": "pending",
    "total_amount": 89.99,
    "shipping_address": "123 Main St",
    "payment_method": "card",
    "items": [
      {
        "product_id": 1,
        "product_name": "T-Shirt",
        "quantity": 2,
        "price": 29.99
      }
    ]
  }
}
```

### 4. User Profile

#### Get Profile
```
GET /users/profile
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "address": "123 Main St",
    "phone": "+1234567890",
    "cash_balance": 100.00,
    "role": "user",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

#### Update Profile
```
PUT /users/profile
Authorization: Bearer <token>

Request:
{
  "name": "John Updated",
  "address": "456 Oak Ave",
  "phone": "+0987654321"
}

Response (200):
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "name": "John Updated",
    "address": "456 Oak Ave",
    "phone": "+0987654321"
  }
}
```

#### Change Password
```
POST /users/change-password
Authorization: Bearer <token>

Request:
{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "confirm_password": "NewPass123!"
}

Response (200):
{
  "success": true,
  "message": "Password changed successfully"
}
```

### 5. Reviews

#### Create Review
```
POST /reviews
Authorization: Bearer <token>

Request:
{
  "product_id": 1,
  "rating": 5,
  "comment": "Excellent product, highly recommended!"
}

Response (201):
{
  "success": true,
  "message": "Review created successfully",
  "data": {
    "review_id": 1
  }
}
```

#### Get Product Reviews
```
GET /reviews/{product_id}?page=1&per_page=10

Response (200):
{
  "success": true,
  "data": {
    "reviews": [
      {
        "id": 1,
        "user_name": "John",
        "rating": 5,
        "comment": "Great!",
        "is_verified_purchase": true,
        "created_at": "2024-01-01T00:00:00"
      }
    ],
    "pagination": {...}
  }
}
```

### 6. Admin - Dashboard

#### Get Dashboard
```
GET /admin/dashboard
Authorization: Bearer <admin_token>

Response (200):
{
  "success": true,
  "data": {
    "users": {
      "total": 150,
      "active": 145,
      "inactive": 5
    },
    "products": {
      "total": 200,
      "active": 195,
      "inactive": 5
    },
    "orders": {
      "total": 500,
      "pending": 50,
      "completed": 400,
      "avg_value": 89.99
    },
    "revenue": {
      "total": 45000.00,
      "this_month": 8500.00
    },
    "recent_orders": [...],
    "low_stock_products": [...]
  }
}
```

### 7. Admin - Product Management

#### Create Product
```
POST /admin/products
Authorization: Bearer <admin_token>

Request:
{
  "name": "New Product",
  "description": "Product description",
  "price": 49.99,
  "category": "Clothing",
  "stock": 100,
  "sizes": ["S", "M", "L", "XL"]
}

Response (201):
{
  "success": true,
  "data": { "product_id": 1 }
}
```

#### Update Product
```
PUT /admin/products/{id}
Authorization: Bearer <admin_token>

Request:
{
  "name": "Updated Name",
  "price": 59.99,
  "stock": 150
}

Response (200):
{
  "success": true,
  "message": "Product updated successfully"
}
```

#### Upload Product Image
```
POST /admin/products/{id}/images
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

Parameters:
  image (file) - JPEG/PNG only, max 16MB
  alt_text (string, optional)
  is_primary (boolean, optional)

Response (201):
{
  "success": true,
  "data": {
    "image_id": 1,
    "image_url": "/uploads/products/image.jpg"
  }
}
```

### 8. Admin - Promo Code Management

#### Create Promo Code
```
POST /admin/promo-codes
Authorization: Bearer <admin_token>

Request:
{
  "code": "SAVE10",
  "discount_type": "percentage",
  "discount_value": 10,
  "expiration_date": "2024-12-31T23:59:59",
  "usage_limit": 100,
  "min_order_amount": 50.00
}

Response (201):
{
  "success": true,
  "data": {
    "promo_code_id": 1,
    "code": "SAVE10"
  }
}
```

### 9. Admin - Activity Logs

#### Get Activity Logs
```
GET /admin/logs?page=1&per_page=20&action=LOGIN&user_id=1
Authorization: Bearer <admin_token>

Response (200):
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 1,
        "user_id": 1,
        "action": "LOGIN",
        "resource": "auth",
        "ip_address": "192.168.1.1",
        "status": "SUCCESS",
        "timestamp": "2024-01-01T00:00:00"
      }
    ],
    "pagination": {...}
  }
}
```

### 10. Admin - User Management

#### List Users
```
GET /admin/users?page=1&per_page=20
Authorization: Bearer <admin_token>

Response (200):
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "user",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00"
      }
    ],
    "pagination": {...}
  }
}
```

#### Update User
```
PUT /admin/users/{id}
Authorization: Bearer <admin_token>

Request:
{
  "is_active": true,
  "cash_balance": 500.00
}

Response (200):
{
  "success": true,
  "message": "User updated successfully"
}
```

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| VALIDATION_ERROR | 400 | Input validation failed |
| INVALID_CREDENTIALS | 401 | Invalid email or password |
| UNAUTHORIZED | 401 | Token required or invalid |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| DUPLICATE_CODE | 409 | Resource already exists |
| OUT_OF_STOCK | 400 | Product out of stock |
| WEAK_PASSWORD | 400 | Password doesn't meet requirements |
| INVALID_FILE_TYPE | 400 | Invalid file format |
| FETCH_ERROR | 500 | Failed to retrieve data |
| CREATE_ERROR | 500 | Failed to create resource |
| UPDATE_ERROR | 500 | Failed to update resource |
| DELETE_ERROR | 500 | Failed to delete resource |

## Rate Limiting

- **Default:** 200 requests per day, 50 requests per hour
- **Specific endpoints:** Limited to 30/60 per minute
- Headers returned:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Best Practices

1. **Always validate input** on both client and server
2. **Use HTTPS** in production
3. **Rotate tokens** regularly
4. **Log all API calls** for audit trailing
5. **Monitor API usage** for suspicious activity
6. **Keep secrets secure** - never commit API keys
7. **Implement timeouts** for long-running requests
8. **Cache responses** where appropriate

## Testing

```bash
# Using curl
curl -X GET http://localhost:5000/api/v1/products \
  -H "Authorization: Bearer <token>"

# Using Python
import requests
headers = {"Authorization": "Bearer <token>"}
response = requests.get("http://localhost:5000/api/v1/products", headers=headers)
```

## Versioning

API versioning is done via URL path: `/api/v1/`  
Future versions will use: `/api/v2/`, `/api/v3/`, etc.

---

**Last Updated:** 2024-01-01  
**API Version:** 1.0.0
