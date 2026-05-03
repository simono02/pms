import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    console.log('Token available:', !!token);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Authorization header set');
    } else {
      console.log('No token found in localStorage');
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// URLs that should NOT trigger auto-logout on 401
// (background calls where we want to silently fail)
const SILENT_401_URLS = [
  '/user/profile',
];

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      const requestUrl = error.config?.url || '';
      const isSilent = SILENT_401_URLS.some(url => requestUrl.includes(url));

      if (!isSilent) {
        // Only hard-logout for real auth failures, not background profile refreshes
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }

    const errorMessage =
      error.response?.data?.error ||
      error.response?.data?.message ||
      error.message ||
      'An error occurred';

    return Promise.reject(new Error(errorMessage));
  }
);

export default api;