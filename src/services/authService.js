import api from './api';

const authService = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  getToken: () => {
    return localStorage.getItem('token');
  },

  setAuthData: (token, user) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  },

  isAuthenticated: () => {
    const token = authService.getToken();
    return !!token;
  },

  refreshToken: async () => {
    try {
      const response = await api.post('/auth/refresh');
      const { token } = response;
      localStorage.setItem('token', token);
      return token;
    } catch (error) {
      authService.logout();
      throw error;
    }
  },

  verifyEmail: async (token) => {
    const response = await api.post('/auth/verify-email', { token });
    return response;
  },

  forgotPassword: async (email) => {
    const response = await api.post('/auth/forgot-password', { email });
    return response;
  },

  resetPassword: async (token, newPassword) => {
    const response = await api.post('/auth/reset-password', { token, newPassword });
    return response;
  },

  changePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/auth/change-password', { currentPassword, newPassword });
    return response;
  }
};

export default authService;
