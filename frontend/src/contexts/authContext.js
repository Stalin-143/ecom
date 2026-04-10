import { create } from 'zustand';
import axiosInstance from '../services/api';

export const useAuthStore = create((set) => ({
  isAuthenticated: !!localStorage.getItem('access_token'),
  user: (() => {
    try {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    } catch {
      return null;
    }
  })(),
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await axiosInstance.post('/auth/login', { email, password });
      const { access_token, refresh_token, user: userData } = response.data.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      set({ isAuthenticated: true, user: userData, loading: false });
      return true;
    } catch (error) {
      set({ error: error.response?.data?.message || 'Login failed', loading: false });
      return false;
    }
  },

  register: async (name, email, password) => {
    set({ loading: true, error: null });
    try {
      await axiosInstance.post('/auth/register', { name, email, password });
      set({ loading: false });
      return true;
    } catch (error) {
      set({ error: error.response?.data?.message || 'Registration failed', loading: false });
      return false;
    }
  },

  logout: async () => {
    try {
      await axiosInstance.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      set({ isAuthenticated: false, user: null });
    }
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    try {
      const response = await axiosInstance.get('/auth/me');
      set({ isAuthenticated: true, user: response.data.data });
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      set({ isAuthenticated: false, user: null });
    }
  },

  updateUser: (userData) => {
    try {
      const stored = localStorage.getItem('user');
      const currentUser = stored ? JSON.parse(stored) : {};
      const updatedUser = { ...currentUser, ...userData };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      set({ user: updatedUser });
    } catch (error) {
      console.error('Error updating user:', error);
    }
  },
}));
