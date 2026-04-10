# E-Commerce Frontend

Modern, responsive React-based frontend with separate user and admin panels.

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API URL
```

### 3. Start Development Server
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Features

### User Panel
- ✓ User registration and secure login
- ✓ Product browsing and filtering
- ✓ Product search and category navigation
- ✓ Product detail pages with reviews
- ✓ Add/manage product reviews
- ✓ Shopping cart functionality
- ✓ Order placement and tracking
- ✓ User profile management
- ✓ Password change functionality
- ✓ Responsive design

### Admin Panel
- ✓ Dashboard with analytics
- ✓ Product CRUD operations
- ✓ Product image upload
- ✓ Category management
- ✓ User management
- ✓ Promo code management
- ✓ Activity log monitoring
- ✓ System metrics and insights

## Project Structure

```
src/
├── components/          # Reusable React components
│   ├── Header.jsx
│   ├── ProtectedRoute.jsx
│   └── ...
├── contexts/            # State management with Zustand
│   └── authContext.js
├── pages/               # Page components
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── user/            # User panel pages
│   │   ├── Dashboard.jsx
│   │   ├── ProductListing.jsx
│   │   ├── ProductDetail.jsx
│   │   ├── Profile.jsx
│   │   └── Orders.jsx
│   └── admin/           # Admin panel pages
│       ├── Dashboard.jsx
│       ├── Products.jsx
│       ├── Users.jsx
│       ├── PromoCodeManagement.jsx
│       └── ActivityLogs.jsx
├── services/            # API client
│   └── api.js
├── styles/              # Global styles
│   └── index.css
├── App.jsx              # Main app component
└── index.js             # Entry point
```

## Technologies Used

- **React 18** - UI framework
- **React Router** - Client-side routing
- **Zustand** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **React Hot Toast** - Notifications
- **Lucide React** - Icons

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

## Docker

Build and run the frontend in Docker:

```bash
docker build -t ecommerce-frontend .
docker run -p 3000:3000 ecommerce-frontend
```

Or use docker-compose from the root directory:

```bash
docker-compose up frontend
```

## Security Features

✓ JWT authentication with token refresh
✓ Secure password validation
✓ Input sanitization
✓ Protected routes based on roles
✓ Secure cookie handling
✓ Automatic logout on token expiration
✓ XSS protection via React
✓ CSRF token integration (ready)

## Performance Optimizations

- Code splitting with React Router
- Lazy loading of components
- Optimized image loading
- Minified CSS with Tailwind
- Client-side caching
- Debounced search requests

## Environment Variables

```
REACT_APP_API_URL=http://localhost:5000/api/v1
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

Proprietary - All rights reserved
