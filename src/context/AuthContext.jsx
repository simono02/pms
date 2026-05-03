import React, { createContext, useContext, useReducer, useEffect } from 'react';
import authService from '../services/authService';
import userService from '../services/userService';

const AuthContext = createContext();

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true, error: null };
    case 'LOGIN_SUCCESS':
      return { ...state, user: action.payload.user, token: action.payload.token, isAuthenticated: true, loading: false, error: null };
    case 'LOGIN_FAILURE':
      return { ...state, user: null, token: null, isAuthenticated: false, loading: false, error: action.payload };
    case 'LOGOUT':
      return { ...state, user: null, token: null, isAuthenticated: false, loading: false, error: null };
    case 'UPDATE_USER':
      return { ...state, user: { ...state.user, ...action.payload } };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: true,
  error: null,
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = () => {
    // Synchronous — just read from localStorage, no API call on init.
    // This prevents the logout cascade where getProfile() returns 401
    // and api.js wipes localStorage before AuthContext can catch it.
    try {
      const token = authService.getToken();
      const savedUser = authService.getCurrentUser();

      if (token && savedUser) {
        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: { user: savedUser, token },
        });
      } else {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Call this manually when you want to sync the latest profile from the server
  const refreshProfile = async () => {
    try {
      const token = authService.getToken();
      const currentUser = await userService.getProfile();
      dispatch({ type: 'UPDATE_USER', payload: currentUser });
      if (token) authService.setAuthData(token, { ...state.user, ...currentUser });
    } catch (err) {
      console.warn('Profile refresh failed (non-critical):', err.message);
    }
  };

  const login = async (email, password) => {
    try {
      dispatch({ type: 'LOGIN_START' });

      const response = await authService.login(email, password);
      console.log('Login response:', response); // Debug log
      
      const { tokens, user: userData } = response;
      const token = tokens?.access_token || response.access_token;

      console.log('Extracted token:', token); // Debug log
      console.log('User data:', userData); // Debug log

      if (!token) throw new Error('No token received from server');

      authService.setAuthData(token, userData);
      dispatch({ type: 'LOGIN_SUCCESS', payload: { user: userData, token } });

      return response;
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE', payload: error.message });
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      dispatch({ type: 'LOGIN_START' });
      const response = await authService.register(userData);
      dispatch({ type: 'SET_LOADING', payload: false });
      return response;
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE', payload: error.message });
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    dispatch({ type: 'LOGOUT' });
  };

  const updateUser = (userData) => {
    dispatch({ type: 'UPDATE_USER', payload: userData });
    if (state.token) {
      authService.setAuthData(state.token, { ...state.user, ...userData });
    }
  };

  const refreshToken = async () => {
    try {
      const token = await authService.refreshToken();
      dispatch({ type: 'LOGIN_SUCCESS', payload: { user: state.user, token } });
      return token;
    } catch (error) {
      dispatch({ type: 'LOGOUT' });
      throw error;
    }
  };

  const hasRole = (role) => state.user?.role === role;

  const canAccess = (requiredRole) => {
    if (!state.user) return false;
    if (state.user.role === 'admin') return true;
    return state.user.role === requiredRole;
  };

  const clearError = () => dispatch({ type: 'CLEAR_ERROR' });

  const value = {
    ...state,
    login,
    register,
    logout,
    updateUser,
    refreshToken,
    refreshProfile,
    hasRole,
    canAccess,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};

export { AuthContext };
export default AuthContext;