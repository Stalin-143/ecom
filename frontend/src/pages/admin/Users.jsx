import React, { useState } from 'react';

const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-6">User Management</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">Manage platform users here.</p>
      </div>
    </div>
  );
};

export default AdminUsers;
