import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../../services/api';
import { useAuthStore } from '../../contexts/authContext';
import toast from 'react-hot-toast';

const UserProfile = () => {
  const { user, updateUser } = useAuthStore();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: user?.name || '',
    address: user?.address || '',
    phone: user?.phone || '',
  });
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleFormChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePasswordChange = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value,
    });
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axiosInstance.put('/users/profile', formData);
      updateUser(formData);
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('New passwords do not match');
      setLoading(false);
      return;
    }

    try {
      await axiosInstance.post('/users/change-password', passwordData);
      toast.success('Password changed successfully');
      setPasswordData({
        old_password: '',
        new_password: '',
        confirm_password: '',
      });
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">My Profile</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Profile Information */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Profile Information</h2>

          <form onSubmit={handleUpdateProfile} className="space-y-4">
            <div>
              <label className="label">Name</label>
              <input
                type="text"
                name="name"
                className="input"
                value={formData.name}
                onChange={handleFormChange}
                required
              />
            </div>

            <div>
              <label className="label">Email</label>
              <input
                type="email"
                className="input"
                value={user?.email}
                disabled
              />
              <p className="text-sm text-gray-500 mt-1">Email cannot be changed</p>
            </div>

            <div>
              <label className="label">Address</label>
              <textarea
                name="address"
                className="input"
                value={formData.address}
                onChange={handleFormChange}
                rows="3"
                placeholder="Enter your address"
              />
            </div>

            <div>
              <label className="label">Phone</label>
              <input
                type="tel"
                name="phone"
                className="input"
                value={formData.phone}
                onChange={handleFormChange}
                placeholder="Enter your phone number"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full disabled:opacity-50"
            >
              {loading ? 'Updating...' : 'Update Profile'}
            </button>
          </form>
        </div>

        {/* Change Password */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Change Password</h2>

          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="label">Current Password</label>
              <input
                type="password"
                name="old_password"
                className="input"
                value={passwordData.old_password}
                onChange={handlePasswordChange}
                required
              />
            </div>

            <div>
              <label className="label">New Password</label>
              <input
                type="password"
                name="new_password"
                className="input"
                value={passwordData.new_password}
                onChange={handlePasswordChange}
                required
                placeholder="Min 8 characters, with uppercase, lowercase, number, and special character"
              />
            </div>

            <div>
              <label className="label">Confirm New Password</label>
              <input
                type="password"
                name="confirm_password"
                className="input"
                value={passwordData.confirm_password}
                onChange={handlePasswordChange}
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full disabled:opacity-50"
            >
              {loading ? 'Changing...' : 'Change Password'}
            </button>
          </form>

          {/* Account Information */}
          <div className="mt-8 pt-8 border-t">
            <h3 className="text-lg font-semibold mb-4">Account Information</h3>
            <p className="text-gray-600 mb-2">
              <strong>Role:</strong> {user?.role || 'User'}
            </p>
            <p className="text-gray-600 mb-2">
              <strong>Cash Balance:</strong> ${user?.cash_balance || 0}
            </p>
            <p className="text-gray-600">
              <strong>Member Since:</strong>{' '}
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
