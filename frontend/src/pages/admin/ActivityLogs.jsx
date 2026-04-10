import React, { useState, useEffect } from 'react';
import axiosInstance from '../../services/api';
import toast from 'react-hot-toast';

const AdminLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-6">Activity Logs</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">View system activity logs here.</p>
      </div>
    </div>
  );
};

export default AdminLogs;
