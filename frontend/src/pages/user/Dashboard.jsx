import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart, User, Package, Zap, Heart, Truck, Award } from 'lucide-react';

const UserDashboard = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 text-white py-20 px-6">
        <div className="container mx-auto">
          <h1 className="text-5xl font-bold mb-6">Welcome Back!</h1>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl">
            Discover amazing products, track your orders, and enjoy exclusive deals. Your shopping experience starts here.
          </p>
          <Link to="/products" className="btn bg-white text-blue-600 hover:bg-gray-100">
            <ShoppingCart size={20} />
            Start Shopping
          </Link>
        </div>
      </section>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-16">
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {/* Browse Products Card */}
          <Link 
            to="/products" 
            className="card-hover group"
          >
            <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Package size={24} className="text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900">Browse Products</h3>
            <p className="text-gray-600 text-sm mb-4">
              Explore our wide range of products across multiple categories
            </p>
            <span className="inline-flex items-center text-blue-600 font-semibold group-hover:translate-x-2 transition-transform">
              Shop now →
            </span>
          </Link>

          {/* My Orders Card */}
          <Link 
            to="/orders" 
            className="card-hover group"
          >
            <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-green-200 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <ShoppingCart size={24} className="text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900">My Orders</h3>
            <p className="text-gray-600 text-sm mb-4">
              Track your orders and view complete order history
            </p>
            <span className="inline-flex items-center text-green-600 font-semibold group-hover:translate-x-2 transition-transform">
              View orders →
            </span>
          </Link>

          {/* Profile Card */}
          <Link 
            to="/profile" 
            className="card-hover group"
          >
            <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-purple-200 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <User size={24} className="text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900">My Profile</h3>
            <p className="text-gray-600 text-sm mb-4">
              Update your personal information and preferences
            </p>
            <span className="inline-flex items-center text-purple-600 font-semibold group-hover:translate-x-2 transition-transform">
              Edit profile →
            </span>
          </Link>
        </div>

        {/* Why Shop With Us */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Why Shop With Us?</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-xl p-6 border border-gray-100 text-center hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap size={24} className="text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Fast Delivery</h3>
              <p className="text-gray-600 text-sm">Quick and reliable shipping to your doorstep</p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-100 text-center hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Award size={24} className="text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Quality Assured</h3>
              <p className="text-gray-600 text-sm">100% authentic and quality-checked products</p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-100 text-center hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart size={24} className="text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Customer Care</h3>
              <p className="text-gray-600 text-sm">24/7 customer support and assistance</p>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-100 text-center hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Truck size={24} className="text-orange-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Easy Returns</h3>
              <p className="text-gray-600 text-sm">Hassle-free returns and refunds policy</p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-2xl p-12 text-center border border-blue-200">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to Shop?</h2>
          <p className="text-gray-700 mb-8 max-w-2xl mx-auto">
            Browse our latest collection and find exactly what you're looking for
          </p>
          <Link to="/products" className="btn btn-primary">
            <ShoppingCart size={20} />
            Explore Products
          </Link>
        </section>
      </div>
    </div>
  );
};

export default UserDashboard;
