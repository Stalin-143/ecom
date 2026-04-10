import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../contexts/authContext';
import { LogOut, ShoppingCart, User, Settings, Menu, X, Home, Package, Users, Tag, BarChart3 } from 'lucide-react';

const Header = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isAdmin = user?.role === 'admin';

  return (
    <header className="sticky top-0 z-50 bg-white shadow-lg border-b border-gray-100">
      <nav className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link 
            to="/" 
            className="flex items-center gap-2 group"
          >
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-2 rounded-lg group-hover:shadow-lg transition-shadow">
              <ShoppingCart size={24} className="text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent">
              ShopHub
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {!isAdmin ? (
              <>
                <Link 
                  to="/products" 
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-2 group"
                >
                  <Package size={18} className="group-hover:text-blue-600" />
                  Products
                </Link>
                <Link 
                  to="/orders" 
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-2 group"
                >
                  <ShoppingCart size={18} className="group-hover:text-blue-600" />
                  Orders
                </Link>
              </>
            ) : (
              <>
                <Link 
                  to="/admin" 
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-2 group"
                >
                  <BarChart3 size={18} className="group-hover:text-blue-600" />
                  Dashboard
                </Link>
                <Link 
                  to="/admin/products" 
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-2 group"
                >
                  <Package size={18} className="group-hover:text-blue-600" />
                  Products
                </Link>
                <Link 
                  to="/admin/users" 
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-2 group"
                >
                  <Users size={18} className="group-hover:text-blue-600" />
                  Users
                </Link>
                <Link 
                  to="/admin/promos" 
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-2 group"
                >
                  <Tag size={18} className="group-hover:text-blue-600" />
                  Promos
                </Link>
              </>
            )}
          </div>

          {/* User Menu */}
          <div className="hidden md:flex items-center gap-6 border-l border-gray-200 pl-8">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                {user?.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900">{user?.name || 'User'}</p>
                <p className="text-xs text-gray-500 capitalize">{user?.role || 'customer'}</p>
              </div>
            </div>
            <Link 
              to="/profile" 
              className="text-gray-600 hover:text-blue-600 transition-colors p-2 hover:bg-blue-50 rounded-lg"
              title="Profile"
            >
              <User size={20} />
            </Link>
            <button
              onClick={handleLogout}
              className="text-gray-600 hover:text-red-600 transition-colors p-2 hover:bg-red-50 rounded-lg"
              title="Logout"
            >
              <LogOut size={20} />
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-gray-600"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pt-4 border-t border-gray-200 space-y-3">
            {!isAdmin ? (
              <>
                <Link 
                  to="/products" 
                  className="block text-gray-700 hover:text-blue-600 font-medium py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Products
                </Link>
                <Link 
                  to="/orders" 
                  className="block text-gray-700 hover:text-blue-600 font-medium py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Orders
                </Link>
              </>
            ) : (
              <>
                <Link 
                  to="/admin" 
                  className="block text-gray-700 hover:text-blue-600 font-medium py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <Link 
                  to="/admin/products" 
                  className="block text-gray-700 hover:text-blue-600 font-medium py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Products
                </Link>
                <Link 
                  to="/admin/users" 
                  className="block text-gray-700 hover:text-blue-600 font-medium py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Users
                </Link>
                <Link 
                  to="/admin/promos" 
                  className="block text-gray-700 hover:text-blue-600 font-medium py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Promos
                </Link>
              </>
            )}
            <hr className="my-3" />
            <Link 
              to="/profile" 
              className="block text-gray-700 hover:text-blue-600 font-medium py-2"
              onClick={() => setMobileMenuOpen(false)}
            >
              Profile
            </Link>
            <button
              onClick={() => {
                handleLogout();
                setMobileMenuOpen(false);
              }}
              className="block w-full text-left text-gray-700 hover:text-red-600 font-medium py-2"
            >
              Logout
            </button>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;
