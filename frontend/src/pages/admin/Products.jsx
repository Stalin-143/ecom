import React, { useState } from 'react';

const AdminProducts = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-6">Product Management</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">Manage your product inventory here.</p>
      </div>
    </div>
  );
};

export default AdminProducts;
