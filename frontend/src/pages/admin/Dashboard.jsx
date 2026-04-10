import React, { useState, useEffect } from 'react';
import axiosInstance from '../../services/api';
import toast from 'react-hot-toast';

const AdminDashboard = () => {
  const [dashboard, setDashboard] = useState({
    users: { total: 0, active: 0 },
    products: { total: 0, active: 0 },
    orders: { total: 0, pending: 0 },
    revenue: { total: 0, this_month: 0 },
    recent_orders: [],
    low_stock_products: [],
    top_products: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.get('/admin/dashboard');
      if (response.data.data) {
        setDashboard(response.data.data);
      }
    } catch (error) {
      console.log('Using default dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="container mx-auto px-4 py-8 text-center">Loading dashboard...</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Admin Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <p className="text-gray-600 text-sm">Total Users</p>
          <p className="text-3xl font-bold text-blue-600">{dashboard.users.total}</p>
          <p className="text-sm text-gray-500 mt-2">{dashboard.users.active} active</p>
        </div>

        <div className="card">
          <p className="text-gray-600 text-sm">Total Products</p>
          <p className="text-3xl font-bold text-green-600">{dashboard.products.total}</p>
          <p className="text-sm text-gray-500 mt-2">{dashboard.products.active} active</p>
        </div>

        <div className="card">
          <p className="text-gray-600 text-sm">Total Orders</p>
          <p className="text-3xl font-bold text-purple-600">{dashboard.orders.total}</p>
          <p className="text-sm text-gray-500 mt-2">{dashboard.orders.pending} pending</p>
        </div>

        <div className="card">
          <p className="text-gray-600 text-sm">Total Revenue</p>
          <p className="text-3xl font-bold text-yellow-600">${dashboard.revenue.total.toFixed(2)}</p>
          <p className="text-sm text-gray-500 mt-2">This month: ${dashboard.revenue.this_month.toFixed(2)}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Recent Orders */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Recent Orders</h2>
          <div className="space-y-4">
            {dashboard.recent_orders.map((order) => (
              <div key={order.id} className="flex justify-between items-center border-b pb-4 last:border-b-0">
                <div>
                  <p className="font-semibold">Order #{order.id}</p>
                  <p className="text-sm text-gray-600">{order.user}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-blue-600">${order.amount.toFixed(2)}</p>
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                    {order.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Low Stock Products */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Low Stock Products</h2>
          <div className="space-y-4">
            {dashboard.low_stock_products.length === 0 ? (
              <p className="text-gray-600">All products have sufficient stock</p>
            ) : (
              dashboard.low_stock_products.map((product) => (
                <div key={product.id} className="flex justify-between items-center border-b pb-4 last:border-b-0">
                  <p className="font-semibold">{product.name}</p>
                  <span className="px-3 py-1 bg-red-100 text-red-800 rounded font-medium">
                    {product.stock} left
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
